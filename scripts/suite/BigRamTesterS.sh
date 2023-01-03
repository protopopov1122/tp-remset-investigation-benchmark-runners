#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

BINDIR="$BENCHMARK_TMPDIR/bin"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
RUNS=10

mkdir -p "$GC_LOGS"
if [[ "x$JFR_ENABLE" == "xtrue" ]]; then
    JFR_DIR="$BENCHMARK_RESULT_DIR/jfr"
    mkdir -p "$JFR_DIR"
fi

"$JAVA_HOME/bin/javac" -d "$BINDIR" "$BENCHMARK_SUITE_BASE_DIR/BigRamTesterS.java"

cd "$BINDIR"

info "Executing $RUNS test run(s)"
for i in $(seq $RUNS); do
    HEAP_FLAGS="-Xmx8G -Xms8G -XX:-UseLargePages"
    JAVA_OPTIONS="$JAVA_OPTIONS $HEAP_FLAGS" _JAVA_OPTIONS="$_JAVA_OPTIONS $HEAP_FLAGS" JAVA_OPTS="$JAVA_OPTS $HEAP_FLAGS" \
    "$JAVA_HOME/bin/java" $(java_gc_log_flags $GC_LOGS/$i.log) $(jfr_flags $JFR_DIR) BigRamTesterS
done