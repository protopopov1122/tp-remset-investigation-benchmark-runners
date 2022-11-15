#!/usr/bin/env bash

export BENCHMARK_SUITE_DIR="$(dirname $0)"

source "$BENCHMARK_SUITE_DIR/scripts/common.sh"
source "$BENCHMARK_SUITE_DIR/scripts/preamble.sh"
source "$BENCHMARK_SUITE_DIR/scripts/env_info.sh"
source "$BENCHMARK_SUITE_DIR/scripts/suite.sh"

initialize_result_env_info
initialize_benchmark_suite
execute_benchmark_suite