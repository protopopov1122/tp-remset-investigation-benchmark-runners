import csv
from pathlib import Path
from typing import Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class SPECjvm2008(AbstractBenchmark):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'specjvm2008')
        self._load_results()

    def get_results(self) -> Dict[int, List[float]]:
        return self._data

    def _load_results(self):
        self._data = dict()
        with open(self._directory.joinpath('results.csv')) as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvReader) # Skip header
            for row in csvReader:
                name = row[0]
                result = float(row[1])
                self._data[name] = result
