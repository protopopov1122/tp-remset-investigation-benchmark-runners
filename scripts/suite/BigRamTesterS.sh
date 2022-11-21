#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

BINDIR="$BENCHMARK_TMPDIR/bin"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
RUNS=10

mkdir -p "$GC_LOGS"

"$JAVA_HOME/bin/javac" -d "$BINDIR" "$BENCHMARK_SUITE_BASE_DIR/BigRamTesterS.java"

cd "$BINDIR"

info "Executing $RUNS test run(s)"
for i in $(seq $RUNS); do
    "$JAVA_HOME/bin/java" -Xmx8G -Xms8G $(java_gc_log_flags $GC_LOGS/$i.log) BigRamTesterS
done