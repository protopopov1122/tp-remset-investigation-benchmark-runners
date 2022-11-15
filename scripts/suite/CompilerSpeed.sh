#!/usr/bin/env bash

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

TMPFILE="$BENCHMARK_TMPDIR/output.log"
RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
PHYSICAL_CORES="$(lscpu --parse='core' | grep -v '#' | sort | uniq | wc -l)"
SHORT_RUNS=6
MEDIUM_RUNS=3
LONG_RUNS=2

info "Detected $PHYSICAL_CORES physical CPU cores on the machine"

echo "Time limit,Threads,Actual time,Compiles/Sec" > "$RESULTS"

run_bench () {
    local time_limit="$1"
    local cores="$2"

    cd "$BENCHMARK_SUITE_BASE_DIR/CompilerSpeed"
    java -jar "dist/CompilerSpeed.jar" "$time_limit" "$cores" | tee "$TMPFILE"
    local time="$(sed -nr 's/^Time:\s*([0-9]+([,\.][0-9]+)?)s.*$/\1/p' $TMPFILE | tr ',' '.')"
    local compiles="$(sed -nr 's/.*\s([0-9]+([,\.][0-9]+)?)\s*compiles\/s$/\1/p' $TMPFILE | tr ',' '.')"

    echo "$1,$2,$time,$compiles" >> "$RESULTS"
}

info "Executing $SHORT_RUNS short test run(s)"
for i in $(seq $SHORT_RUNS); do
    run_bench 15 "$PHYSICAL_CORES"
done

info "Executing $MEDIUM_RUNS medium test run(s)"
for i in $(seq $MEDIUM_RUNS); do
    run_bench 60 "$PHYSICAL_CORES"
done

info "Executing $LONG_RUNS long test run(s)"
for i in $(seq $LONG_RUNS); do
    run_bench 180 "$PHYSICAL_CORES"
done
