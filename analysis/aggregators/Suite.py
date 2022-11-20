from pathlib import Path
from aggregators.Util import ResultAggregator, ResultExporter
from benchmarks.Suite import BenchmarkSuite
from aggregators.CompilerSpeed import CompilerSpeedAggregator
from aggregators.DelayInducer import DelayInducerAggregator
from aggregators.DaCapo import DaCapoAggregator
from aggregators.Renaissance import RenaissainceAggregator
from aggregators.SPECjvm2008 import SPECjvm2008Aggregator
from aggregators.SPECjbb2005 import SPECjbb2005Aggregator
from aggregators.pjbb2005 import pjbb2005Aggregator
from aggregators.Optaplanner import OptaplannerAggregator

class BenchmarkSuiteAggregator(ResultAggregator, ResultExporter):
    def __init__(self) -> None:
        super().__init__()
        self._compiler_speed = CompilerSpeedAggregator()
        self._delay_inducer = DelayInducerAggregator()
        self._dacapo = DaCapoAggregator()
        self._renaissance = RenaissainceAggregator()
        self._specjvm = SPECjvm2008Aggregator()
        self._jbb2005 = SPECjbb2005Aggregator()
        self._pjbb2005 = pjbb2005Aggregator()
        self._optaplanner = OptaplannerAggregator()

    def update(self, suite: BenchmarkSuite):
        self._compiler_speed.update(suite.get_compiler_speed())
        self._delay_inducer.update(suite.get_delay_inducer())
        self._dacapo.update(suite.get_dacapo())
        self._renaissance.update(suite.get_renaissance())
        self._specjvm.update(suite.get_specjvm2008())
        self._jbb2005.update(suite.get_specjbb2005())
        self._pjbb2005.update(suite.get_pjbb2005())
        self._optaplanner.update(suite.get_optaplanner())

    def get_result(self):
        return {
            'CompilerSpeed': self._compiler_speed.get_result(),
            'DelayInducer': self._delay_inducer.get_result(),
            'DaCapo': self._dacapo.get_result(),
            'Renaissance': self._renaissance.get_result(),
            'SPECjvm2008': self._specjvm.get_result(),
            'SPECjbb2005': self._jbb2005.get_result(),
            'pjbb2005': self._pjbb2005.get_result(),
            'Optaplanner': self._optaplanner.get_result()
        }

    def export_result(self, destination: Path):
        if destination.exists():
            raise RuntimeError(f'Export destination {destination} already exists')
        destination.mkdir()
        self._do_export(destination, 'CompilerSpeed.csv', self._compiler_speed)
        self._do_export(destination, 'DelayInducer.csv', self._delay_inducer)
        self._do_export(destination, 'DaCapo.csv', self._dacapo)
        self._do_export(destination, 'Renaissance.csv', self._renaissance)
        self._do_export(destination, 'SPECjvm2008.csv', self._specjvm)
        self._do_export(destination, 'SPECjbb2005.csv', self._jbb2005)
        self._do_export(destination, 'pjbb2005_time.csv', self._pjbb2005, False)
        self._do_export(destination, 'pjbb2005_throughput.csv', self._pjbb2005, True)
        self._do_export(destination, 'Optaplanner.csv', self._optaplanner)

    def _do_export(self, destination: Path, name: str, exporter: ResultExporter, *extra_args):
        with destination.joinpath(name).open('w') as output:
            exporter.export_result(output, *extra_args)
