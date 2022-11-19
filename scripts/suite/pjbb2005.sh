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
    -propfile "$BENCHMARK_RESOURCES/SPECjbb.props" 2>&1 | tee "$TMPFILE"

echo "Operation,msec" > "$RESULTS"
cat "$TMPFILE" | sed -nr 's/=+\s*(pjbb2005)\s*PASSED\s*in\s*([0-9]+)\s*msec\s*=+/\1,\2/p' >> "$RESULTS"
