#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS1="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
TMPFILE="$BENCHMARK_TMPDIR/output.log"

declare -A BENCHMARKS=(
    ["h2"]="3000M"
)

mkdir "$GC_LOGS"
if [[ "x$JFR_ENABLE" == "xtrue" ]]; then
    JFR_DIR="$BENCHMARK_RESULT_DIR/jfr"
    mkdir -p "$JFR_DIR"
fi

cd "$BENCHMARK_TMPDIR"

for BENCHMARK_NAME in "${!BENCHMARKS[@]}"; do
    HEAP_SIZE="${BENCHMARKS[$BENCHMARK_NAME]}"
    info "Running DaCapo $BENCHMARK_NAME with $HEAP_SIZE heap"
    HEAP_FLAGS="-Xmx$HEAP_SIZE -Xms$HEAP_SIZE"
    if [[ "x$JFR_ENABLE" == "xtrue" ]]; then
        mkdir -p "$JFR_DIR/$BENCHMARK_NAME"
    fi
    JAVA_OPTIONS="$JAVA_OPTIONS $HEAP_FLAGS" _JAVA_OPTIONS="$_JAVA_OPTIONS $HEAP_FLAGS" JAVA_OPTS="$JAVA_OPTS $HEAP_FLAGS" \
    $JAVA_HOME/bin/java $(java_gc_log_flags $GC_LOGS/$BENCHMARK_NAME.gc.log) $(jfr_flags $JFR_DIR/$BENCHMARK_NAME) \
        -jar "$BENCHMARK_SUITE_BASE_DIR/dacapo-9.12-MR1-bach.jar" \
        -s huge -C "$BENCHMARK_NAME" \
        2>&1 | tee -a "$TMPFILE"
done

echo "Benchmark,Time (msec)" > "$RESULTS1"
cat "$TMPFILE" | sed -nr 's/=+\s*DaCapo*\s[a-zA-Z0-9\.+-]+\s*([a-zA-Z0-9]+)\s*PASSED\s*in\s*([0-9]+)\s*msec\s*=+/\1,\2/p' >> "$RESULTS1"