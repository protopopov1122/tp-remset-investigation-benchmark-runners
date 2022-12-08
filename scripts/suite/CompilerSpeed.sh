#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

TMPFILE="$BENCHMARK_TMPDIR/output.log"
RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
PHYSICAL_CORES="$(lscpu --parse='core' | grep -v '#' | sort | uniq | wc -l)"
SHORT_RUNS=20
MEDIUM_RUNS=10
LONG_RUNS=5

info "Detected $PHYSICAL_CORES physical CPU cores on the machine"

mkdir -p "$GC_LOGS"
if [[ "x$JFR_ENABLE" == "xtrue" ]]; then
    JFR_DIR="$BENCHMARK_RESULT_DIR/jfr"
    mkdir -p "$JFR_DIR"
fi
echo "Time limit,Threads,Actual time,Compiles/Sec" > "$RESULTS"

run_bench () {
    local time_limit="$1"
    local cores="$2"
    local counter="$3"

    cd "$BENCHMARK_SUITE_BASE_DIR/CompilerSpeed"
    java $(java_gc_log_flags $GC_LOGS/$time_limit-$cores-$i.log) $(jfr_flags $JFR_DIR) -jar "dist/CompilerSpeed.jar" "$time_limit" "$cores" | tee "$TMPFILE"
    local time="$(sed -nr 's/^Time:\s*([0-9]+([,\.][0-9]+)?)s.*$/\1/p' $TMPFILE | tr ',' '.')"
    local compiles="$(sed -nr 's/.*\s([0-9]+([,\.][0-9]+)?)\s*compiles\/s$/\1/p' $TMPFILE | tr ',' '.')"

    echo "$1,$2,$time,$compiles" >> "$RESULTS"
}

info "Executing $SHORT_RUNS short test run(s)"
for i in $(seq $SHORT_RUNS); do
    run_bench 15 "$PHYSICAL_CORES" "$i"
done

info "Executing $MEDIUM_RUNS medium test run(s)"
for i in $(seq $MEDIUM_RUNS); do
    run_bench 60 "$PHYSICAL_CORES" "$i"
done

info "Executing $LONG_RUNS long test run(s)"
for i in $(seq $LONG_RUNS); do
    run_bench 180 "$PHYSICAL_CORES" "$i"
done
