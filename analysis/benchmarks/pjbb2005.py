import csv
from pathlib import Path
from typing import Tuple, Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class pjbb2005(AbstractBenchmark):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'pjbb2005')
        self._load_results()

    def get_results(self) -> Tuple[List[float], Dict[int, List[float]]]:
        return (self._time, self._throughputs)

    def _load_results(self):
        self._time = list()
        self._throughputs = dict()
        with open(self._directory.joinpath('results1.csv')) as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvReader) # Skip header
            for row in csvReader:
                self._time.append(float(row[1]))
        with open(self._directory.joinpath('results2.csv')) as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvReader) # Skip header
            for row in csvReader:
                warehouses = int(row[0])
                throughput = float(row[1])
                self._throughputs[warehouses] = throughput
