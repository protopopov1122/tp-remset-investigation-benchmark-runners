#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS_CSV="$BENCHMARK_RESULT_DIR/results.csv"
GC_LOGS="$BENCHMARK_RESULT_DIR/gc_logs"
JBB2005="$BENCHMARK_SUITE_BASE_DIR/jbb2005"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
TMPFILE2="$BENCHMARK_TMPDIR/tmp1"
TMPFILE3="$BENCHMARK_TMPDIR/tmp2"

export CLASSPATH="$JBB2005/jbb.jar:$JBB2005/check.jar:$CLASSPATH"

mkdir "$GC_LOGS"
cd "$JBB2005"
$JAVA_HOME/bin/java \
    $(java_gc_log_flags $GC_LOGS/gc.log) \
    -cp "$JBB2005/jbb.jar:$JBB2005/check.jar" \
    spec.jbb.JBBmain \
    -propfile "$BENCHMARK_RESOURCES/SPECjbb.props" | tee "$TMPFILE"

cp -r "$JBB2005/results" "$BENCHMARK_RESULT_DIR"

cat "$TMPFILE" | sed -nr 's/TOTALS\s+FOR:\s*COMPANY\s+with\s+([0-9]+)\s*warehouses/\1/p' > "$TMPFILE2"
cat "$TMPFILE" | sed -nr 's/.*throughput\s*=\s*([0-9]+(\.[0-9]+)?)\s*SPECjbb2005\s+bops.*/\1/p' > "$TMPFILE3"
(echo "warehouses,throughput"; paste -d, "$TMPFILE2" "$TMPFILE3" | tr -d ' ') > "$RESULTS_CSV"