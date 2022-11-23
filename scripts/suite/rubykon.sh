#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
TMPFILE="$BENCHMARK_TMPDIR/output.log"

export JAVA_OPTIONS="$JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.log)"
"$BENCHMARK_SUITE_BASE_DIR/rubykon/jruby-9.3.9.0/bin/jruby" \
    -Xcompile.invokedynamic=true \
    -J-Xms1500m \
    -J-Xmx1500m \
    "$BENCHMARK_SUITE_BASE_DIR/rubykon/rubykon/benchmark/mcts_avg.rb" | tee "$TMPFILE"

echo "Run,Size,Iterations,Performance,Time,Precision" > "$RESULTS"
cat "$TMPFILE" | \
    sed -nr 's/([0-9]+x[0-9]+)\s+([0-9_]+)\s*iterations\s*([0-9]+(\.[0-9]+)?)\s*i\/min\s*([0-9]+(\.[0-9]+)?)\s*s\s*\(avg\)\s*\(.\s*([0-9]+(\.[0-9]+))%\)/\1,\2,\3,\5,\7/p' | \
    sed '1 s/^/warmup,/ ; 2 s/^/runtime,/' >> "$RESULTS"
