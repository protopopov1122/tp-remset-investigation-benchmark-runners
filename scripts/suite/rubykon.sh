#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
RUNS=5

mkdir -p "$GC_LOGS"

run_rubykon () {
    export JAVA_OPTIONS="$JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.$1.log)"
    export _JAVA_OPTIONS="$_JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.$1.log)"
    export JAVA_OPTS="$JAVA_OPTS $(java_gc_log_flags $GC_LOGS/gc.$1.log)"

    "$BENCHMARK_SUITE_BASE_DIR/rubykon/jruby-9.3.9.0/bin/jruby" \
        -Xcompile.invokedynamic=true \
        -J-Xms1500m \
        -J-Xmx1500m \
        "$BENCHMARK_SUITE_BASE_DIR/rubykon/rubykon/benchmark/mcts_avg.rb"  | tee "$TMPFILE"

    cat "$TMPFILE" | \
        sed -nr 's/([0-9]+x[0-9]+)\s+([0-9_]+)\s*iterations\s*([0-9]+(\.[0-9]+)?)\s*i\/min\s*([0-9]+(\.[0-9]+)?)\s*s\s*\(avg\)\s*\(.\s*([0-9]+(\.[0-9]+))%\)/\1,\2,\3,\5,\7/p' | \
        sed "1 s/^/$1,warmup,/ ; 2 s/^/$1,runtime,/" >> "$RESULTS"
}

echo "Run,Type,Size,Iterations,Performance,Time,Precision" > "$RESULTS"

info "Executing $RUNS test run(s)"
for i in $(seq $RUNS); do
    run_rubykon "$i"
done
