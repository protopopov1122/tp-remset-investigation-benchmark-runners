#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"

mkdir "$GC_LOGS"
mkdir "$BENCHMARK_TMPDIR/jdk"
mkdir "$BENCHMARK_TMPDIR/maven"

ln -s "$JAVA_HOME" "$BENCHMARK_TMPDIR/jdk/benchmarked"

cd "$BENCHMARK_TMPDIR"
tar -xf "$BENCHMARK_SUITE_BASE_DIR/optaplanner/apache-maven-3.8.6-bin.tar.gz" -C ./maven/

cp "$BENCHMARK_SUITE_BASE_DIR/optaplanner/optaplanner_custom.sh" .
export JAVA_OPTIONS="$JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.log)"
export _JAVA_OPTIONS="$_JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.log)"
export JAVA_OPTS="$JAVA_OPTS $(java_gc_log_flags $GC_LOGS/gc.log)"
./optaplanner_custom.sh "$BENCHMARK_SUITE_BASE_DIR/optaplanner"

cp -r "$BENCHMARK_TMPDIR/results" "$BENCHMARK_RESULT_DIR"