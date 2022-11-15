export BENCHMARK_SUITE_RUNNER_SCRIPT_DIR="$BENCHMARK_SUITE_RUNNER_DIR/scripts/suite"
declare -A BENCHMARK_SUITE_RUNNER=()
declare -A BENCHMARK_PARAMETERS=()

add_all_benchmarks_to_suite () {
    for benchmark_script in $BENCHMARK_SUITE_RUNNER_SCRIPT_DIR/*.sh; do
        local script_path="$(realpath $benchmark_script)"
        local script_basename="$(basename $script_path)"
        local benchmark_name="${script_basename%.*}"
        local benchmark_params=""

        if [[ "x${BENCHMARK_SUITE_RUNNER[$benchmark_name]}" == "x" ]]; then
            BENCHMARK_SUITE_RUNNER[$benchmark_name]="$script_path"
            BENCHMARK_PARAMETERS[$benchmark_name]="$benchmark_params"
        fi
    done
}

initialize_benchmark_suite () {
    while IFS=',' read -ra benchmark_specs; do
        for benchmark_spec in "${benchmark_specs[@]}"; do
            if [[ "x$benchmark_spec" == "xALL" ]]; then
                add_all_benchmarks_to_suite
                continue
            fi

            local benchmark_name="$(echo $benchmark_spec | awk -F: '{ print $1 }')"
            local benchmark_params="$(echo $benchmark_spec | awk -F: '{ print $2 }')"
            local script_path="$(realpath -m $BENCHMARK_SUITE_RUNNER_SCRIPT_DIR/$benchmark_name.sh)"
            if [[ ! -f "$script_path" ]]; then
                warn "Cannot find benchmark matching specification $benchmark_spec"
            else
                BENCHMARK_SUITE_RUNNER[$benchmark_name]="$script_path"
                BENCHMARK_PARAMETERS[$benchmark_name]="$benchmark_params"
            fi
        done
    done <<< "$BENCHMARK_SUITE_RUNNER_SPEC"

    info "$(printf 'Benchmarks matching spec \"%s\":' $BENCHMARK_SUITE_RUNNER_SPEC)"
    for benchmark_name in "${!BENCHMARK_SUITE_RUNNER[@]}"; do
        local benchmark_params="${BENCHMARK_PARAMETERS[$benchmark_name]}"
        local benchmark_script="${BENCHMARK_SUITE_RUNNER[$benchmark_name]}"

        append_runner_script_configuration "$benchmark_name" "$benchmark_script" "$benchmark_params"
        info "\t$benchmark_name($benchmark_params) at $benchmark_script"
    done
}

execute_benchmark_suite () {
    for benchmark_name in "${!BENCHMARK_SUITE_RUNNER[@]}"; do
        local benchmark_params="${BENCHMARK_PARAMETERS[$benchmark_name]}"
        local benchmark_script="${BENCHMARK_SUITE_RUNNER[$benchmark_name]}"

        export BENCHMARK_NAME="$benchmark_name"
        export BENCHMARK_RESULT_DIR="$BENCHMARK_SUITE_RUNNER_RESULT_DIR/benchmarks/$benchmark_name"
        export BENCHMARK_TMPDIR="$BENCHMARK_SUITE_RUNNER_RESULT_DIR/tmp"
        local benchmark_output="$BENCHMARK_RESULT_DIR/output.log"
        local benchmark_timestamps="$BENCHMARK_RESULT_DIR/timestamps.log"

        mkdir -p "$BENCHMARK_RESULT_DIR"
        mkdir -p "$BENCHMARK_TMPDIR"

        info "Starting benchmark $benchmark_name"
        info "\tBenchmark result directory is $BENCHMARK_RESULT_DIR"
        info "\tOutput saved to $benchmark_output"
        info "\tTimestamps stored in $benchmark_timestamps"
        date "+%s" > "$benchmark_timestamps"

        "$benchmark_script" "$benchmark_params" 2>&1 | tee "$benchmark_output"
        local exit_code="$?"

        date "+%s" >> "$benchmark_timestamps"
        
        if [[ "x$exit_code" == "x0" ]]; then
            info "Benchmark $benchmark_name has finished successfully"
        else
            warn "Benchmark $benchmark_name has failed with exit code $exit_code"
        fi

        rm -rf "$BENCHMARK_TMPDIR"
    done
}
