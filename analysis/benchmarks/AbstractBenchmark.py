from abc import ABC, abstractmethod
from pathlib import Path

class AbstractBenchmark(ABC):
    def __init__(self, base_dir: Path, name: str):
        self._directory = base_dir.joinpath('benchmarks', name).resolve()
        if not self._directory.exists():
            raise RuntimeError(f'Benchmark result directory {self._directory} does not exist')
        if self._directory.joinpath('failed').exists():
            raise RuntimeError(f'Benchmark {self._directory.name} had failed')

    def name(self) -> str:
        return self._directory.name

    def get_result_dir(self) -> Path:
        return self._directory

    @abstractmethod
    def get_results(self): pass
