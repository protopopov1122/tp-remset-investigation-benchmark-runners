from aggregators.Util import ResultAggregator
from comparators.CompilerSpeed import CompilerSpeedComparator
from comparators.DelayInducer import DelayInducerComparator
from comparators.DaCapo import DaCapoComparator
from comparators.Optaplanner import OptaplannerComparator
from comparators.pjbb2005 import pjbb2005Comparator
from comparators.Renaissance import RenaissanceComparator
from comparators.SPECjbb2005 import SPECjbb2005Comparator
from comparators.SPECjvm2008 import SPECjvm2008Comparator

class BenchmarkSuiteComparator(ResultAggregator):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._compiler_speed = CompilerSpeedComparator(self._baseline['CompilerSpeed'])
        self._delay_inducer = DelayInducerComparator(self._baseline['DelayInducer'])
        self._dacapo = DaCapoComparator(self._baseline['DaCapo'])
        self._optaplanner = OptaplannerComparator(self._baseline['Optaplanner'])
        self._pjbb2005 = pjbb2005Comparator(self._baseline['pjbb2005'])
        self._renaissance = RenaissanceComparator(self._baseline['Renaissance'])
        self._specjbb2005 = SPECjbb2005Comparator(self._baseline['SPECjbb2005'])
        self._specjvm2008 = SPECjvm2008Comparator(self._baseline['SPECjvm2008'])
    
    def update(self, measurement):
        self._compiler_speed.update(measurement['CompilerSpeed'])
        self._delay_inducer.update(measurement['DelayInducer'])
        self._dacapo.update(measurement['DaCapo'])
        self._optaplanner.update(measurement['Optaplanner'])
        self._pjbb2005.update(measurement['pjbb2005'])
        self._renaissance.update(measurement['Renaissance'])
        self._specjbb2005.update(measurement['SPECjbb2005'])
        self._specjvm2008.update(measurement['SPECjvm2008'])

    def get_result(self):
        return {
            'CompilerSpeed': self._compiler_speed.get_result(),
            'DelayInducer': self._delay_inducer.get_result(),
            'DaCapo': self._dacapo.get_result(),
            'Optaplanner': self._optaplanner.get_result(),
            'pjbb2005': self._pjbb2005.get_result(),
            'Renaissance': self._renaissance.get_result(),
            'SPECjbb2005': self._specjbb2005.get_result(),
            'SPECjvm2008': self._specjvm2008.get_result()
        }
