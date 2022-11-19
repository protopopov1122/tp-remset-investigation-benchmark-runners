#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS1="$BENCHMARK_RESULT_DIR/results1.csv"
RESULTS2="$BENCHMARK_RESULT_DIR/results2.csv"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
TMPFILE2="$BENCHMARK_TMPDIR/tmp1"
TMPFILE3="$BENCHMARK_TMPDIR/tmp2"
PJBB2005=""$BENCHMARK_SUITE_BASE_DIR/pjbb2005""

export CLASSPATH="$PJBB2005/jbb.jar:$PJBB2005/check.jar:$CLASSPATH"

$JAVA_HOME/bin/java \
    -cp "$PJBB2005/jbb.jar:$PJBB2005/check.jar" \
    spec.jbb.JBBmain \
    -propfile "$BENCHMARK_RESOURCES/SPECjbb.props" 2>&1 | tee "$TMPFILE"

echo "Operation,msec" > "$RESULTS1"
cat "$TMPFILE" | sed -nr 's/=+\s*(pjbb2005)\s*PASSED\s*in\s*([0-9]+)\s*msec\s*=+/\1,\2/p' >> "$RESULTS1"

cat "$TMPFILE" | sed -nr 's/TOTALS\s+FOR:\s*COMPANY\s+with\s+([0-9]+)\s*warehouses/\1/p' > "$TMPFILE2"
cat "$TMPFILE" | sed -nr 's/.*throughput\s*=\s*([0-9]+(\.[0-9]+)?)\s*SPECjbb2005\s+bops.*/\1/p' > "$TMPFILE3"
(echo "warehouses,throughput"; paste -d, "$TMPFILE2" "$TMPFILE3" | tr -d ' ') > "$RESULTS2"
