#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

BINDIR="$BENCHMARK_TMPDIR/bin"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
RESULTS="$BENCHMARK_RESULT_DIR/results"
RUNS=10

mkdir -p "$RESULTS"

"$JAVA_HOME/bin/javac" -d "$BINDIR" "$BENCHMARK_SUITE_BASE_DIR/BigRamTesterS.java"

cd "$BINDIR"

info "Executing $RUNS test run(s)"
for i in $(seq $RUNS); do
    "$JAVA_HOME/bin/java" -Xmx8G -Xms8G -Xlog:async -Xlog:gc=debug,gc+start=debug,gc+phases*=debug,gc+heap=debug:"$RESULTS/$i.log" BigRamTesterS
done