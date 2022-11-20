import csv
from pathlib import Path
from typing import Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class Renaissance(AbstractBenchmark):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'renaissance')
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
                duration = int(row[1])
                uptime = int(row[2])
                start = int(row[3])
                if name not in self._data:
                    self._data[name] = list()
                self._data[name].append({
                    'duration': duration,
                    'uptime': uptime,
                    'start': start
                })
