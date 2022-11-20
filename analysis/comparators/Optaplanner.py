from aggregators.Util import ResultAggregator
from comparators.Util import make_numeric_comparison

class OptaplannerComparator(ResultAggregator):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()

    def update(self, measurement):
        comparison = dict()
        for key, score in measurement.items():
            if key not in self._baseline:
                continue
            baseline_score = self._baseline[key]
            comparison[key] = make_numeric_comparison(baseline_score, score)
        self._data.append(comparison)
    
    def get_result(self):
        return self._data
