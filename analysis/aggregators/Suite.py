import io
import zipfile
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
from aggregators.Rubykon import RubykonAggregator

class BenchmarkSuiteAggregator(ResultAggregator, ResultExporter):
    def __init__(self) -> None:
        super().__init__()
        self._compiler_speed = CompilerSpeedAggregator()
        self._delay_inducer = DelayInducerAggregator()
        self._dacapo = DaCapoAggregator()
        self._dacapo_large = DaCapoAggregator()
        self._dacapo_huge = DaCapoAggregator()
        self._renaissance = RenaissainceAggregator()
        self._specjvm = SPECjvm2008Aggregator()
        self._jbb2005 = SPECjbb2005Aggregator()
        self._pjbb2005 = pjbb2005Aggregator()
        self._optaplanner = OptaplannerAggregator()
        self._rubykon = RubykonAggregator()

    def update(self, suite: BenchmarkSuite):
        self._compiler_speed.update(suite.get_compiler_speed())
        self._delay_inducer.update(suite.get_delay_inducer())
        self._dacapo.update(suite.get_dacapo())
        self._dacapo_large.update(suite.get_dacapo_large())
        self._dacapo_huge.update(suite.get_dacapo_huge())
        self._renaissance.update(suite.get_renaissance())
        self._specjvm.update(suite.get_specjvm2008())
        self._jbb2005.update(suite.get_specjbb2005())
        self._pjbb2005.update(suite.get_pjbb2005())
        self._optaplanner.update(suite.get_optaplanner())
        self._rubykon.update(suite.get_rubykon())

    def get_result(self):
        return {
            'CompilerSpeed': self._compiler_speed.get_result(),
            'DelayInducer': self._delay_inducer.get_result(),
            'DaCapo': self._dacapo.get_result(),
            'DaCapoLarge': self._dacapo_large.get_result(),
            'DaCapoHuge': self._dacapo_huge.get_result(),
            'Renaissance': self._renaissance.get_result(),
            'SPECjvm2008': self._specjvm.get_result(),
            'SPECjbb2005': self._jbb2005.get_result(),
            'pjbb2005': self._pjbb2005.get_result(),
            'Optaplanner': self._optaplanner.get_result(),
            'Rubykon': self._rubykon.get_result()
        }

    def export_result(self, destination):
        with zipfile.ZipFile(destination, 'w') as archive:
            self._do_export(archive, 'CompilerSpeed.csv', self._compiler_speed)
            self._do_export(archive, 'DelayInducer.csv', self._delay_inducer)
            self._do_export(archive, 'DaCapo.csv', self._dacapo)
            self._do_export(archive, 'DaCapoLarge.csv', self._dacapo_large)
            self._do_export(archive, 'DaCapoHuge.csv', self._dacapo_huge)
            self._do_export(archive, 'Renaissance.csv', self._renaissance)
            self._do_export(archive, 'SPECjvm2008.csv', self._specjvm)
            self._do_export(archive, 'SPECjbb2005.csv', self._jbb2005)
            self._do_export(archive, 'pjbb2005_time.csv', self._pjbb2005, False)
            self._do_export(archive, 'pjbb2005_throughput.csv', self._pjbb2005, True)
            self._do_export(archive, 'Optaplanner.csv', self._optaplanner)
            self._do_export(archive, 'Rubykon.csv', self._rubykon)

    def _do_export(self, archive: zipfile.ZipFile, name: str, exporter: ResultExporter, *extra_args):
        content = io.StringIO()
        exporter.export_result(content, *extra_args)
        archive.writestr(name, content.getvalue())
