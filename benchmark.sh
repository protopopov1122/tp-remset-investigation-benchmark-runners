#!/usr/bin/env bash
# Benchmark suite runner script entry point
# Usage:
# ./benchmark.sh SPEC [RUN-ID]
# Where SPEC is a comma-separated list of benchmark runner names with optional parameter (delimited by colon after benchmark name),
# or ALL to run all benchmark runners, and RUN-ID is an identifier for result directory (optional - "run" is used as default name).
# Additionally, following environment variables are supported:
#   * JAVA_HOME - directory containing JDK image for benchmarking (mandatory).
#   * JAVA_OPTIONS - JVM options to be passed to the benchmarks (optional, empty by default).
#   * BENCHMARK_SUITE_BASE_DIR - directory containing actual benchmarks (mandatory).
#   * BENCHMARK_SUITE_RUNNER_RESULT_DIR - directory to contain benchmarking results (optional, the default value is "./results/[RUN-ID]-xxxxxxxxx")
#   * BENCHMARK_SUITE_RUNNER_NOTES - free-form string to be saved along with benchmarking results (optional, empty by default).
#   * LOG_ENABLE_COLORS - (yes/no) whether to enable colourful logging output (enabled by default).
# Running the benchmarking suite will produce a directory that contains benchmarking results, raw benchmark output, timestamps, as well
# as some general information about the machine and runner setup.

export BENCHMARK_SUITE_RUNNER_DIR="$(dirname $0)"

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"
source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/preamble.sh"
source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/configuration.sh"
source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/suite.sh"

write_runner_configuration
initialize_benchmark_suite
execute_benchmark_suite

export BENCHMARK_SUITE_RUNNER_END_TIMESTAMP="$(date '+%s')"
info "Benchmark suite finished at $BENCHMARK_SUITE_RUNNER_END_TIMESTAMP"
record_finish_timestamp "$BENCHMARK_SUITE_RUNNER_END_TIMESTAMP"
