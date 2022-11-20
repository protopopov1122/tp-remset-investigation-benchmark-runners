from aggregators.Util import ResultAggregator
from comparators.Util import make_numeric_comparison

class CompilerSpeedComparator(ResultAggregator):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()

    def update(self, measurement):
        comparison = dict()
        for duration, ops_per_sec in measurement.items():
            if duration not in self._baseline:
                continue
            baseline_ops_per_sec = self._baseline[duration]
            comparison[duration] = make_numeric_comparison(baseline_ops_per_sec, ops_per_sec)
        self._data.append(comparison)
    
    def get_result(self):
        return self._data
