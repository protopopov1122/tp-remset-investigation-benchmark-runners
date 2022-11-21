# Code for initial suite runner configuration

load_java_home_configuration () {
    if [[ "x$JAVA_HOME" == "x" ]]; then
        fatal "JAVA_HOME environment variable is not defined"
    fi

    if [[ ! -d "$JAVA_HOME" ]]; then
        fatal "JAVA_HOME directory $JAVA_HOME does not exist"
    fi

    export _JAVA_HOME="$JAVA_HOME"
    export JAVA="$JAVA_HOME"
    export _JAVA="$JAVA_HOME"
    export PATH="$JAVA_HOME/bin:$PATH"
}

load_benchmark_suite_base_dir_configuration () {
    if [[ "x$BENCHMARK_SUITE_BASE_DIR" == "x" ]]; then
        fatal "BENCHMARK_SUITE_BASE_DIR environment variable is not defined"
    fi

    if [[ ! -d "$BENCHMARK_SUITE_BASE_DIR" ]]; then
        fatal "BENCHMARK_SUITE_BASE_DIR directory $BENCHMARK_SUITE_BASE_DIR does not exist"
    fi
}

load_benchmark_suite_runner_spec () {
    export BENCHMARK_SUITE_RUNNER_SPEC="$1"
    if [[ "x$BENCHMARK_SUITE_RUNNER_SPEC" == "x" ]]; then
        fatal "Benchmarks are not specified in the command line"
    fi
}

load_java_options () {
    if [[ "x$JAVA_OPTIONS" == "x" ]]; then
        warn "JAVA_OPTIONS environment variable is not defined. Using default options"
        export JAVA_OPTIONS=""
    fi

    if [[ "x$JAVA_TOOL_OPTIONS" == "x" ]]; then
        warn "JAVA_TOOL_OPTIONS environment variable is not defined. Using default options"
        export JAVA_TOOL_OPTIONS=""
    fi

    export _JAVA_OPTIONS="$JAVA_OPTIONS"
    export JAVA_OPTS="$JAVA_OPTIONS"
}

load_benchmark_suite_runner_output_configuration () {
    if [[ "x$BENCHMARK_SUITE_RUNNER_OUTPUT_DIR" == "x" ]]; then
        local BENCHMARK_SUITE_RUNNER_RESULT_DIR_PREFIX="$1"
        if [[ "x$BENCHMARK_SUITE_RUNNER_RESULT_DIR_PREFIX" == "x" ]]; then
            BENCHMARK_SUITE_RUNNER_RESULT_DIR_PREFIX="run"
        fi

        if [[ "x$BENCHMARK_SUITE_RUNNER_RESULTS" == "x" ]]; then
            export BENCHMARK_SUITE_RUNNER_RESULTS="$BENCHMARK_SUITE_RUNNER_DIR/results"
        fi

        local BENCHMARK_SUITE_RUNNER_RESULT_DIRNAME="$BENCHMARK_SUITE_RUNNER_RESULT_DIR_PREFIX-$(date -d @$BENCHMARK_SUITE_RUNNER_START_TIMESTAMP '+%Y%m%d%H%M%S')"
        local BENCHMARK_SUITE_RUNNER_RESULT_DIRPATH="$BENCHMARK_SUITE_RUNNER_RESULTS/$BENCHMARK_SUITE_RUNNER_RESULT_DIRNAME"

        export BENCHMARK_SUITE_RUNNER_OUTPUT_DIR="$(realpath -m $BENCHMARK_SUITE_RUNNER_RESULT_DIRPATH)"
    elif [[ -d "$BENCHMARK_SUITE_RUNNER_OUTPUT_DIR" ]]; then
        fatal "BENCHMARK_SUITE_RUNNER_OUTPUT_DIR directory $BENCHMARK_SUITE_RUNNER_OUTPUT_DIR already exists"

        export BENCHMARK_SUITE_RUNNER_RESULTS=""
    fi
}

report_benchmark_suite_runner_configuration () {
    info "Benchmark suite started at $BENCHMARK_SUITE_RUNNER_START_TIMESTAMP"
    info "Benchmark suite configured with benchmarks: $BENCHMARK_SUITE_RUNNER_SPEC"
    info "Benchmark suite configured with JAVA_HOME=$JAVA_HOME"
    info "Benchmark suite configured with JAVA_OPTIONS=$JAVA_OPTIONS"
    info "Benchmark suite configured with BENCHMARK_SUITE_BASE_DIR=$BENCHMARK_SUITE_BASE_DIR"
    info "Benchmark suite configured with BENCHMARK_SUITE_RUNNER_OUTPUT_DIR=$BENCHMARK_SUITE_RUNNER_OUTPUT_DIR"
    info "Benchmark notes: $BENCHMARK_SUITE_RUNNER_NOTES"
}

load_runner_configuration () {
    export BENCHMARK_SUITE_RUNNER_START_TIMESTAMP="$(date '+%s')"

    load_java_home_configuration
    load_benchmark_suite_base_dir_configuration
    load_benchmark_suite_runner_spec "$1"
    load_benchmark_suite_runner_output_configuration "$2"
    load_java_options
    report_benchmark_suite_runner_configuration
}

initialize_runners () {
    mkdir -p "$BENCHMARK_SUITE_RUNNER_OUTPUT_DIR"

    if [[ "x$BENCHMARK_SUITE_RUNNER_RESULTS" != "x" ]]; then
        local BENCHMARK_LATEST_RESULTS_DIR="$BENCHMARK_SUITE_RUNNER_RESULTS/latest"
        rm -f "$BENCHMARK_LATEST_RESULTS_DIR"
        ln -s "$(realpath -m --relative-to=$BENCHMARK_SUITE_RUNNER_RESULTS $BENCHMARK_SUITE_RUNNER_OUTPUT_DIR)" "$BENCHMARK_LATEST_RESULTS_DIR"
    fi

    export BENCHMARK_SUITE_RUNNER_CONFIG_DIR="$BENCHMARK_SUITE_RUNNER_OUTPUT_DIR/conf"
    trace "Directory containing runner configuration: $BENCHMARK_SUITE_RUNNER_CONFIG_DIR"

    mkdir -p "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR"
    cat /proc/cpuinfo > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/cpuinfo.log"
    cat /proc/meminfo > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/meminfo.log"
    cat /etc/issue > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/platform.log"
    uname -a >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/platform.log"
    export | grep "JAVA\|BENCHMARK" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/environment.log"
    echo "$BENCHMARK_SUITE_RUNNER_START_TIMESTAMP" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/timestamps.log"
    echo "$BENCHMARK_SUITE_RUNNER_SPEC" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/runner_spec.log"
    echo "$BENCHMARK_SUITE_RUNNER_NOTES" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/notes.txt"
    echo -e "Name,Script,Parameters" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/runner_scripts.csv"
}

save_runner_script_configuration () {
    local benchmark_name="$1"
    local benchmark_script="$2"
    local benchmark_params="$3"
    echo -e "$benchmark_name,$benchmark_script,$benchmark_params" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/runner_scripts.csv"
}

finalize_runners () {
    export BENCHMARK_SUITE_RUNNER_END_TIMESTAMP="$(date '+%s')"
    echo "$BENCHMARK_SUITE_RUNNER_END_TIMESTAMP" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/timestamps.log"
    info "Benchmark suite finished at $BENCHMARK_SUITE_RUNNER_END_TIMESTAMP"
}

interrupt_runners () {
    if [[ "x$BENCHMARK_SUITE_RUNNER_CONFIG_DIR" != "x" ]]; then
        date "+%s" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/interrupted_at.log"
    fi
}