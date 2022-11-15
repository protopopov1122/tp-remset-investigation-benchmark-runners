export BENCHMARK_SUITE_STARTED_AT="$(date '+%s')"

# Check JAVA_HOME
if [[ "x$JAVA_HOME" == "x" ]]; then
    fatal "JAVA_HOME environment variable is not defined"
fi

if [[ ! -d "$JAVA_HOME" ]]; then
    fatal "JAVA_HOME directory does not exist"
fi

# Check benchmark base dir
if [[ "x$BENCHMARK_BASE_DIR" == "x" ]]; then
    fatal "BENCHMARK_BASE_DIR environment variable is not defined"
fi

if [[ ! -d "$BENCHMARK_BASE_DIR" ]]; then
    fatal "BENCHMARK_BASE_DIR directory does not exist"
fi

# Check benchmark specification
export BENCHMARK_SPEC="$1"
if [[ "x$BENCHMARK_SPEC" == "x" ]]; then
    fatal "Benchmarks are not specified in the command line"
fi

# Save benchmark description
export BENCHMARK_DESCRIPTION="$2"

# Check result directory
if [[ "x$BENCHMARK_SUITE_RESULTS" == "x" ]]; then
    BENCHMARK_SUITE_RESULT_DIRNAME="$BENCHMARK_SUITE_DIR/results/run-$(date -d @$BENCHMARK_SUITE_STARTED_AT '+%Y%m%d%H%M%S')"
    export BENCHMARK_SUITE_RESULTS="$(realpath -m $BENCHMARK_SUITE_RESULT_DIRNAME)"
    mkdir -p "$BENCHMARK_SUITE_RESULTS"

    export BENCHMARK_LATEST_RESULTS="$BENCHMARK_SUITE_DIR/results/latest"
    rm -f "$BENCHMARK_LATEST_RESULTS"
    ln -s "$(realpath -m --relative-to=$BENCHMARK_SUITE_DIR/results $BENCHMARK_SUITE_RESULT_DIRNAME)" "$BENCHMARK_LATEST_RESULTS"
elif [[ -d "$BENCHMARK_SUITE_RESULTS" ]]; then
    fatal "BENCHMARK_SUITE_RESULTS already exists"
fi

# Check Java options
if [[ "x$JAVA_OPTIONS" == "x" ]]; then
    warn "JAVA_OPTIONS environment variable is not defined. Using default options"
    export JAVA_OPTIONS=""
fi

# Report configuration
info "Benchmark suite started at $BENCHMARK_SUITE_STARTED_AT"
info "Benchmark suite configured with benchmarks: $BENCHMARK_SPEC"
info "Benchmark suite configured with JAVA_HOME=$JAVA_HOME"
info "Benchmark suite configured with JAVA_OPTIONS=$JAVA_OPTIONS"
info "Benchmark suite configured with BENCHMARK_BASE_DIR=$BENCHMARK_BASE_DIR"
info "Benchmark suite configured with BENCHMARK_SUITE_RESULTS=$BENCHMARK_SUITE_RESULTS"
info "Benchmark description: $BENCHMARK_DESCRIPTION"

# Initialize
export _JAVA_HOME="$JAVA_HOME"
export _JAVA_OPTIONS="$JAVA_OPTIONS"
export PATH="$JAVA_HOME/bin:$PATH"