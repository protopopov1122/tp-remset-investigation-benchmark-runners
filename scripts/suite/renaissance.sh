#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

declare -A BENCHMARKS=(
    ["page-rank"]="1800M"
    ["future-genetic"]="100M"
    ["akka-uct"]="775M"
    ["movie-lens"]="625M"
    ["scala-doku"]="100M"
    ["chi-square"]="500M"
    ["fj-kmeans"]="500M"
    ["finagle-http"]="100M"
    ["reactors"]="1128M"
    ["dec-tree"]="500M"
    ["naive-bayes"]="3000M"
    ["als"]="550M"
    ["par-mnemonics"]="200M"
    ["scala-kmeans"]="70M"
    ["philosophers"]="60M"
    ["log-regression"]="650M"
    ["gauss-mix"]="500M"
    ["mnemonics"]="160M"
    ["dotty"]="150M"
    ["finagle-chirper"]="250M"
)

GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
TMPFILE="$BENCHMARK_TMPDIR/result.csv"
RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
mkdir "$GC_LOGS"
if [[ "x$JFR_ENABLE" == "xtrue" ]]; then
    JFR_DIR="$BENCHMARK_RESULT_DIR/jfr"
    mkdir -p "$JFR_DIR"
fi

for BENCHMARK_NAME in "${!BENCHMARKS[@]}"; do
    HEAP_SIZE="${BENCHMARKS[$BENCHMARK_NAME]}"
    info "Running Renaissance $BENCHMARK_NAME with $HEAP_SIZE heap"
    HEAP_FLAGS="-Xmx$HEAP_SIZE -Xms$HEAP_SIZE"
    if [[ "x$JFR_ENABLE" == "xtrue" ]]; then
        mkdir -p "$JFR_DIR/$BENCHMARK_NAME"
    fi
    JAVA_OPTIONS="$JAVA_OPTIONS $HEAP_FLAGS" _JAVA_OPTIONS="$_JAVA_OPTIONS $HEAP_FLAGS" JAVA_OPTS="$JAVA_OPTS $HEAP_FLAGS" \
    $JAVA_HOME/bin/java $(java_gc_log_flags $GC_LOGS/$BENCHMARK_NAME.gc.log) $(jfr_flags "$JFR_DIR/$BENCHMARK_NAME") -jar "$BENCHMARK_SUITE_BASE_DIR/renaissance-gpl-0.14.1.jar" \
        --scratch-base "$BENCHMARK_TMPDIR" \
        --csv "$TMPFILE" \
        "$BENCHMARK_NAME"

    if [[ -f "$RESULTS" ]]; then
        tail -n+2 "$TMPFILE" >> "$RESULTS"
    else
        mv "$TMPFILE" "$RESULTS"
    fi
done