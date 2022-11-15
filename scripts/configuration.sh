# Bash functions to preserve suite runner configuration

export BENCHMARK_SUITE_RUNNER_CONFIG_DIR="$BENCHMARK_SUITE_RUNNER_RESULT_DIR/conf"

write_runner_configuration () {
    trace "Directory containing runner configuration: $BENCHMARK_SUITE_RUNNER_CONFIG_DIR"

    mkdir -p "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR"
    cat /proc/cpuinfo > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/cpuinfo.log"
    cat /proc/meminfo > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/meminfo.log"
    echo "JAVA_HOME=\"$JAVA_HOME\"" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/java.log"
    echo "JAVA_OPTIONS=\"$JAVA_OPTIONS\"" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/java.log"
    echo "$BENCHMARK_SUITE_RUNNER_START_TIMESTAMP" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/timestamps.log"
    echo "$BENCHMARK_SUITE_RUNNER_SPEC" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/runner_spec.log"
    echo "$BENCHMARK_SUITE_RUNNER_NOTES" > "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/notes.txt"
    echo -e "Name,Script,Parameters" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/runner_scripts.csv"
}

record_finish_timestamp () {
    echo "$1" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/timestamps.log"
}

append_runner_script_configuration () {
    local benchmark_name="$1"
    local benchmark_script="$2"
    local benchmark_params="$3"
    echo -e "$benchmark_name,$benchmark_script,$benchmark_params" >> "$BENCHMARK_SUITE_RUNNER_CONFIG_DIR/runner_scripts.csv"
}
