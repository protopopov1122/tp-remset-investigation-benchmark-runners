import csv
from pathlib import Path
from typing import Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class Rubykon(AbstractBenchmark):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'rubykon')
        self._load_results()

    def get_results(self) -> Dict[int, List[float]]:
        return self._data

    def _load_results(self):
        self._data = dict()
        with open(self._directory.joinpath('results.csv')) as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvReader) # Skip header
            for row in csvReader:
                tp = row[1]
                if tp != 'runtime':
                    continue
                run = row[0]
                size = row[2]
                iterations = row[3]
                performance = float(row[4])
                self._data[(run, size, iterations)] = performance
