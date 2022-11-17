#!/usr/bin/env bash
# Benchmark suite runner script entry point
# Usage:
# ./run_benchmarks.sh SPEC [RUN-ID]
# Where SPEC is a comma-separated list of benchmark runner names with optional parameter (delimited by colon after benchmark name),
# or ALL to run all benchmark runners, and RUN-ID is an identifier for result directory (optional - "run" is used as default name).
# Additionally, following environment variables are supported:
#   * JAVA_HOME - directory containing JDK image for benchmarking (mandatory).
#   * JAVA_OPTIONS - JVM options to be passed to the benchmarks (optional, empty by default).
#   * BENCHMARK_SUITE_BASE_DIR - directory containing actual benchmarks (mandatory).
#   * BENCHMARK_SUITE_RUNNER_OUTPUT_DIR - directory to contain benchmarking run outputs (optional, the default value is "$BENCHMARK_SUITE_RUNNER_RESULTS/[RUN-ID]-xxxxxxxxx")
#   * BENCHMARK_SUITE_RUNNER_RESULTS - directory with results of mutiple runs (ignored if BENCHMARK_SUITE_RUNNER_OUTPUT_DIR is defined)
#   * BENCHMARK_SUITE_RUNNER_NOTES - free-form string to be saved along with benchmarking results (optional, empty by default).
#   * LOG_ENABLE_COLORS - (yes/no) whether to enable colourful logging output (enabled by default).
# Running the benchmarking suite will produce a directory that contains benchmarking results, raw benchmark output, timestamps, as well
# as some general information about the machine and runner setup.

export BENCHMARK_SUITE_RUNNER_DIR="$(dirname $0)"

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"
source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/configuration.sh"
source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/suite.sh"

stop_benchmark () {
    warn "Benchmark suite runner has been interrupted"
    interrupt_runners
    trap - SIGINT SIGTERM
    kill -- -$$
}

start_benchmark () {
    trap stop_benchmark SIGINT SIGTERM

    load_runner_configuration "$1" "$2"
    initialize_runners
    initialize_benchmark_suite
    execute_benchmark_suite
    finalize_runners
}

start_benchmark "$@"
