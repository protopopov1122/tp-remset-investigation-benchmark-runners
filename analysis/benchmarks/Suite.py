from pathlib import Path
from benchmarks.CompilerSpeed import CompilerSpeed
from benchmarks.DelayInducer import DelayInducer
from benchmarks.DaCapo import DaCapo, DaCapoLarge, DaCapoHuge
from benchmarks.Renaissance import Renaissance
from benchmarks.SPECjvm2008 import SPECjvm2008
from benchmarks.SPECjbb2005 import SPECjbb2005
from benchmarks.pjbb2005 import pjbb2005
from benchmarks.Optaplanner import Optaplanner
from benchmarks.Rubykon import Rubykon

class BenchmarkSuite:
    def __init__(self, base_dir: Path):
        self._base_dir = base_dir.resolve()
        if not self._base_dir.exists():
            raise RuntimeError(f'Benchmark suite result directory {self._base_dir} does not exist')
        self._compiler_speed = None
        self._delay_inducer = None
        self._dacapo = None
        self._dacapo_large = None
        self._dacapo_huge = None
        self._renaissance = None
        self._specjvm = None
        self._jbb2005 = None
        self._pjbb2005 = None
        self._optaplanner = None
        self._rubykon = None

    def get_compiler_speed(self) -> CompilerSpeed:
        return self._instantiate_benchmark('_compiler_speed', CompilerSpeed)

    def get_delay_inducer(self) -> DelayInducer:
        return self._instantiate_benchmark('_delay_inducer', DelayInducer)

    def get_dacapo(self) -> DaCapo:
        return self._instantiate_benchmark('_dacapo', DaCapo)

    def get_dacapo_large(self) -> DaCapoLarge:
        return self._instantiate_benchmark('_dacapo_large', DaCapoLarge)

    def get_dacapo_huge(self) -> DaCapoHuge:
        return self._instantiate_benchmark('_dacapo_huge', DaCapoHuge)

    def get_renaissance(self) -> Renaissance:
        return self._instantiate_benchmark('_renaissance', Renaissance)

    def get_specjvm2008(self) -> SPECjvm2008:
        return self._instantiate_benchmark('_specjvm', SPECjvm2008)

    def get_specjbb2005(self) -> SPECjbb2005:
        return self._instantiate_benchmark('_jbb2005', SPECjbb2005)

    def get_pjbb2005(self) -> pjbb2005:
        return self._instantiate_benchmark('_pjbb2005', pjbb2005)

    def get_optaplanner(self) -> Optaplanner:
        return self._instantiate_benchmark('_optaplanner', Optaplanner)

    def get_rubykon(self) -> Rubykon:
        return self._instantiate_benchmark('_rubykon', Rubykon)
    
    def _instantiate_benchmark(self, field_name, benchmark_class):
        if getattr(self, field_name) is None:
            setattr(self, field_name, benchmark_class(self._base_dir))
        return getattr(self, field_name)
