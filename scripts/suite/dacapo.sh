#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

RESULTS="$BENCHMARK_RESULT_DIR/results.csv"
TMPFILE="$BENCHMARK_TMPDIR/output.log"
INCLUDED="avrora batik biojava eclipse fop graphchi h2 jme jython luindex lusearch pmd sunflow xalan zxing"
EXCLUDED="cassandra h2o kafka tomcat tradebeans tradesoap"

info "Running DaCapo benchmarks: $INCLUDED"
warn "Excluded benchmarks: $EXCLUDED"

cd "$BENCHMARK_TMPDIR"
$JAVA_HOME/bin/java -jar "$BENCHMARK_SUITE_BASE_DIR/dacapo-evaluation-git+309e1fa.jar" \
    $INCLUDED 2>&1 | tee "$TMPFILE"

echo "Benchmark,Time (msec)" > "$RESULTS"
cat "$TMPFILE" | sed -nr 's/=+\s*DaCapo*\s[a-zA-Z0-9+-]+\s*([a-zA-Z0-9]+)\s*PASSED\s*in\s*([0-9]+)\s*msec\s*=+/\1,\2/p' >> "$RESULTS"