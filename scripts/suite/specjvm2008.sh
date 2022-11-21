#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

TMPFILE="$BENCHMARK_TMPDIR/output.log"
RESULTS="$BENCHMARK_RESULT_DIR/results"
RESULTS_CSV="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
SPECJVM2008="$BENCHMARK_SUITE_BASE_DIR/specjvm2008"

mkdir "$GC_LOGS"

export JAVA_OPTS="$JAVA_OPTS $(java_gc_log_flags $GC_LOGS/gc.log) --add-exports=java.xml/jdk.xml.internal=ALL-UNNAMED"
export JAVA_OPTIONS="$JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.log) --add-exports=java.xml/jdk.xml.internal=ALL-UNNAMED"
export _JAVA_OPTIONS="$_JAVA_OPTIONS $(java_gc_log_flags $GC_LOGS/gc.log) --add-exports=java.xml/jdk.xml.internal=ALL-UNNAMED"

cd "$SPECJVM2008"
rm -rf results
sh ./run-specjvm.sh -ikv -ict \
    startup.helloworld startup.compress startup.crypto.aes  \
    startup.crypto.rsa startup.crypto.signverify startup.mpegaudio \
    startup.scimark.fft startup.scimark.lu startup.scimark.monte_carlo \
    startup.scimark.sor startup.scimark.sparse startup.serial startup.sunflow \
    startup.xml.transform startup.xml.validation \
    compress crypto.aes crypto.rsa crypto.signverify derby mpegaudio \
    scimark.fft.large scimark.lu.large scimark.sor.large scimark.sparse.large \
    scimark.fft.small scimark.lu.small scimark.sor.small scimark.sparse.small \
    scimark.monte_carlo serial sunflow xml.transform xml.validation | tee "$TMPFILE"

cp -r "$SPECJVM2008/results" "$RESULTS"

echo "Benchmark,ops/m" > "$RESULTS_CSV"
cat "$TMPFILE" | sed -nr "s/Score\s+on\s+([a-zA-Z0-9\.]*):\s*([0-9]+(\.[0-9]+)?)\s*ops\/m/\1,\2/p" >> "$RESULTS_CSV"
