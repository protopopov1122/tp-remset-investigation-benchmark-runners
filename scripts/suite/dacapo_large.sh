#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
INCLUDED="avrora  h2 jython  lusearch lusearch-fix pmd sunflow xalan"

info "Running DaCapo benchmarks with 'large' size: $INCLUDED"

mkdir "$GC_LOGS"
cd "$BENCHMARK_TMPDIR"
HEAP_SIZES="-Xmx2G -Xms2G"
export JAVA_OPTIONS="$JAVA_OPTIONS $HEAP_SIZES"
export _JAVA_OPTIONS="$_JAVA_OPTIONS $HEAP_SIZES"
export JAVA_OPTS="$JAVA_OPTS $HEAP_SIZES"
$JAVA_HOME/bin/java $(java_gc_log_flags $GC_LOGS/gc.log) -jar "$BENCHMARK_SUITE_BASE_DIR/dacapo-9.12-MR1-bach.jar" \
    -s large $INCLUDED 2>&1 | tee "$TMPFILE"

echo "Benchmark,Time (msec)" > "$RESULTS"
cat "$TMPFILE" | sed -nr 's/=+\s*DaCapo*\s[a-zA-Z0-9\.+-]+\s*([a-zA-Z0-9]+)\s*PASSED\s*in\s*([0-9]+)\s*msec\s*=+/\1,\2/p' >> "$RESULTS"