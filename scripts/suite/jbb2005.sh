#!/usr/bin/env bash

set -e
set -o pipefail

source "$BENCHMARK_SUITE_RUNNER_DIR/scripts/common.sh"

JBB2005=""$BENCHMARK_SUITE_BASE_DIR/jbb2005""

export CLASSPATH="$JBB2005/jbb.jar:$JBB2005/check.jar:$CLASSPATH"

cd "$JBB2005"
$JAVA_HOME/bin/java \
    -cp "$JBB2005/jbb.jar:$JBB2005/check.jar" \
    spec.jbb.JBBmain \
    -propfile "$JBB2005/SPECjbb.props"

cp -r "$JBB2005/results" "$BENCHMARK_RESULT_DIR"
