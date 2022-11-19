#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

mkdir "$BENCHMARK_TMPDIR/jdk"
mkdir "$BENCHMARK_TMPDIR/downloads"
mkdir "$BENCHMARK_TMPDIR/maven"

ln -s "$JAVA_HOME" "$BENCHMARK_TMPDIR/jdk/benchmarked"

cd "$BENCHMARK_TMPDIR/downloads"
wget "https://dlcdn.apache.org/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.tar.gz"

cd "$BENCHMARK_TMPDIR"
tar -xf downloads/apache-maven-3.8.6-bin.tar.gz -C ./maven/

cp "$BENCHMARK_SUITE_BASE_DIR/optaplanner/optaplanner.sh" .
./optaplanner.sh

cp -r "$BENCHMARK_SUITE_BASE_DIR/results" "$BENCHMARK_RESULT_DIR/results"