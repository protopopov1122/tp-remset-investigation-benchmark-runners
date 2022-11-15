#!/usr/bin/env bash

source "$BENCHMARK_SUITE_DIR/scripts/common.sh"

info "Using java: $(which java)"

TMPFILE="$BENCHMARK_TMPDIR/tmp"
RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
run_bench () {
    cd "$BENCHMARK_BASE_DIR/CompilerSpeed"
    java -jar "dist/CompilerSpeed.jar" "$1" "$2" | tee "$TMPFILE"
    local time="$(sed -nr 's/^Time:\s*([0-9]+([,\.][0-9]+)?)s.*$/\1/p' $TMPFILE | tr ',' '.')"
    local compiles="$(sed -nr 's/.*\s([0-9]+([,\.][0-9]+)?)\s*compiles\/s$/\1/p' $TMPFILE | tr ',' '.')"

    echo "$1,$2,$time,$compiles" >> "$RESULTS"
}

echo "Time limit,Threads,Runtime,Compiles/Sec" > "$RESULTS"

PHYSICAL_CORES="$(grep "core id" /proc/cpuinfo | sort | uniq | wc -l)"
run_bench 15 "$PHYSICAL_CORES"
run_bench 15 "$PHYSICAL_CORES"
run_bench 15 "$PHYSICAL_CORES"
