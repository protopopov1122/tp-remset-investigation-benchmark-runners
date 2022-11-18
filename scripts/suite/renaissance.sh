#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

$JAVA_HOME/bin/java -jar "$BENCHMARK_SUITE_BASE_DIR/renaissance-gpl-0.14.1.jar" \
    --scratch-base "$BENCHMARK_TMPDIR" \
    --csv "$BENCHMARK_RESULT_DIR/results.csv" \
    all