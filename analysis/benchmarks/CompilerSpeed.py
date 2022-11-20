import csv
from pathlib import Path
from typing import Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class CompilerSpeed(AbstractBenchmark):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'CompilerSpeed')
        self._load_results()

    def get_results(self) -> Dict[int, List[float]]:
        return self._data

    def _load_results(self):
        self._data = dict()
        with open(self._directory.joinpath('results.csv')) as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvReader) # Skip header
            for row in csvReader:
                time_limit = int(row[0])
                result = float(row[3])
                if time_limit not in self._data:
                    self._data[time_limit] = list()
                self._data[time_limit].append(result)