#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path
from typing import List
from benchmarks.Suite import BenchmarkSuite
from aggregators.Suite import BenchmarkSuiteAggregator

def run_aggregation(argv: List[str]):
    export_output = argv[0]
    suite_results = [BenchmarkSuite(Path(arg)) for arg in argv[1:]]
    aggregator = BenchmarkSuiteAggregator()
    for result in suite_results:
        aggregator.update(result)
    aggregator.export_result(Path(export_output))

if __name__ == '__main__':
    try:
        run_aggregation(sys.argv[1:])
    except:
        traceback.print_exc()
