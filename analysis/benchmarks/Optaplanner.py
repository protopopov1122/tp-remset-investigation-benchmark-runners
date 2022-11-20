import csv
from pathlib import Path
from typing import Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class Optaplanner(AbstractBenchmark):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'optaplanner')
        self._load_results()

    def get_results(self) -> Dict[int, List[float]]:
        return self._data

    def _load_results(self):
        self._data = dict()
        with open(self._directory.joinpath('results', 'summary.csv')) as csvFile:
            csvReader = csv.reader(csvFile)
            next(csvReader) # Skip header
            for row in csvReader:
                gc = row[2]
                solverId = int(row[3])
                score = int(row[5])
                self._data[(gc, solverId)] = score
