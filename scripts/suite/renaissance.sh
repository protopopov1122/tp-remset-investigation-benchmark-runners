#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
mkdir "$GC_LOGS"

$JAVA_HOME/bin/java $(java_gc_log_flags $GC_LOGS/gc.log) -jar "$BENCHMARK_SUITE_BASE_DIR/renaissance-gpl-0.14.1.jar" \
    --scratch-base "$BENCHMARK_TMPDIR" \
    --csv "$BENCHMARK_RESULT_DIR/results.csv" \
    all