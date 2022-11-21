#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path
from typing import List
from benchmarks.Suite import BenchmarkSuite
from aggregators.Suite import BenchmarkSuiteAggregator
from comparators.Suite import BenchmarkSuiteComparator

def run_comparison(argv: List[str]):
    export_path = argv[0]
    separator_index = argv.index('--')
    baseline_suites = [BenchmarkSuite(Path(arg)) for arg in argv[1:separator_index]]
    comparison_suites = [BenchmarkSuite(Path(arg)) for arg in argv[separator_index + 1:]]
    baseline_aggregator = BenchmarkSuiteAggregator()
    comparison_aggregator = BenchmarkSuiteAggregator()
    for suite in baseline_suites:
        baseline_aggregator.update(suite)
    for suite in comparison_suites:
        comparison_aggregator.update(suite)
    comparator = BenchmarkSuiteComparator(baseline_aggregator.get_result())
    comparator.update(comparison_aggregator.get_result())
    comparator.export_result(export_path)

if __name__ == '__main__':
    try:
        run_comparison(sys.argv[1:])
    except:
        traceback.print_exc()
