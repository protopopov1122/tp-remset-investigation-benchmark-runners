#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
PJBB2005=""$BENCHMARK_SUITE_BASE_DIR/pjbb2005""

export CLASSPATH="$PJBB2005/jbb.jar:$PJBB2005/check.jar:$CLASSPATH"

$JAVA_HOME/bin/java \
    -cp "$PJBB2005/jbb.jar:$PJBB2005/check.jar" \
    spec.jbb.JBBmain \
    -propfile "$PJBB2005/SPECjbb-8x50000.props" 2>&1 | tee "$TMPFILE"


echo "Operation,Count,Total,Min,Max,Avg" > "$RESULTS"
cat "$TMPFILE" | sed -nr 's/^\s*New Order:\s*([0-9]+)\s*([0-9]+(\.[0-9]+)?)\s+([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?).*$/New Order,\1,\2,\4,\6,\8/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/^\s*Payment:\s*([0-9]+)\s*([0-9]+(\.[0-9]+)?)\s+([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?).*$/Payment,\1,\2,\4,\6,\8/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/^\s*OrderStatus:\s*([0-9]+)\s*([0-9]+(\.[0-9]+)?)\s+([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?).*$/OrderStatus,\1,\2,\4,\6,\8/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/^\s*Delivery:\s*([0-9]+)\s*([0-9]+(\.[0-9]+)?)\s+([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?).*$/Delivery,\1,\2,\4,\6,\8/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/^\s*Stock Level:\s*([0-9]+)\s*([0-9]+(\.[0-9]+)?)\s+([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?).*$/Stock level,\1,\2,\4,\6,\8/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/^\s*Cust Report:\s*([0-9]+)\s*([0-9]+(\.[0-9]+)?)\s+([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?)\s*([0-9]+(\.[0-9]+)?).*$/Cust Report,\1,\2,\4,\6,\8/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/(throughput)\s*=\s*([0-9]+(\.[0-9]+)?)\s*SPECjbb2005\s+bops/\1,,\2,,,/p' >> "$RESULTS"
cat "$TMPFILE" | sed -nr 's/=+\s*(pjbb2005)\s*PASSED\s*in\s*([0-9]+)\s*msec\s*=+/\1,,\2,,,/p' >> "$RESULTS"
