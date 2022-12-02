import csv
from pathlib import Path
from typing import Dict, List
from benchmarks.AbstractBenchmark import AbstractBenchmark

class DaCapoBase(AbstractBenchmark):
    def __init__(self, base_dir: Path, bench_dir: str):
        super().__init__(base_dir, bench_dir)
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
                result = int(row[1])
                self._data[name] = result

class DaCapo(DaCapoBase):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'dacapo')

class DaCapoLarge(DaCapoBase):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'dacapo_large')

class DaCapoHuge(DaCapoBase):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir, 'dacapo_huge')