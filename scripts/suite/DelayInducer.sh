#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

BINDIR="$BENCHMARK_TMPDIR/bin"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
RUNS=50

"$JAVA_HOME/bin/javac" -d "$BINDIR" "$BENCHMARK_SUITE_BASE_DIR/DelayInducer.java"

echo "Wall clock time (ms)" > "$RESULTS"

run_bench () {
    cd "$BINDIR"
    if [[ -x "/usr/bin/time" ]]; then
        /usr/bin/time -v "$JAVA_HOME/bin/java" DelayInducer 2>&1 | tee "$TMPFILE"
        wallclock_time="$(sed -nr 's/^.*wall clock.*(([0-9]+):([0-9]+)\.([0-9]+))$/\2:\3:\4/p' $TMPFILE | awk -F: '{ print $1*60000+$2*1000+$3*10 }')"
        echo $wallclock_time >> "$RESULTS"
    else
        bash -c 'time $JAVA_HOME/bin/java DelayInducer' 2>&1 | tee "$TMPFILE"
        wallclock_time="$(sed -nr 's/^real\s*(([0-9]+)m([0-9]+)[,\.]([0-9]+)s)$/\2:\3:\4/p' $TMPFILE | awk -F: '{ print $1*60000+$2*1000+$3 }')"
        echo $wallclock_time >> "$RESULTS"
    fi
}

info "Executing $RUNS test run(s)"
for i in $(seq $RUNS); do
    run_bench
done
