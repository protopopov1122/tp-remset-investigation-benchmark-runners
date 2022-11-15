export BENCHMARK_SUITE_RESULT_ENV_DIR="$BENCHMARK_SUITE_RESULTS/env"

initialize_result_env_info () {
    trace "Result envinronment directory: $BENCHMARK_SUITE_RESULT_ENV_DIR"
    mkdir "$BENCHMARK_SUITE_RESULT_ENV_DIR"
    lscpu > "$BENCHMARK_SUITE_RESULT_ENV_DIR/lscpu.log"
    cat /proc/meminfo > "$BENCHMARK_SUITE_RESULT_ENV_DIR/meminfo.log"
    "$JAVA_HOME/bin/java" -version > "$BENCHMARK_SUITE_RESULT_ENV_DIR/java_version.log" 2>&1
    echo "JAVA_HOME=\"$JAVA_HOME\"" > "$BENCHMARK_SUITE_RESULT_ENV_DIR/bench_env.log"
    echo "JAVA_OPTIONS=\"$JAVA_OPTIONS\"" >> "$BENCHMARK_SUITE_RESULT_ENV_DIR/bench_env.log"
    echo "$BENCHMARK_SUITE_STARTED_AT" > "$BENCHMARK_SUITE_RESULT_ENV_DIR/timestamp"
    echo "$BENCHMARK_SPEC" > "$BENCHMARK_SUITE_RESULT_ENV_DIR/bench_spec.log"
    echo "$BENCHMARK_DESCRIPTION" > "$BENCHMARK_SUITE_RESULT_ENV_DIR/description.txt"
}

add_benchmark_to_env_info () {
    local benchmark_name="$1"
    local benchmark_script="$2"
    local benchmark_params="$3"
    echo -e "$benchmark_name,$benchmark_script,$benchmark_params" > "$BENCHMARK_SUITE_RESULT_ENV_DIR/benchmark_scripts.csv"
}
