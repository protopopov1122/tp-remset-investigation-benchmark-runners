from aggregators.Util import ResultAggregator
from comparators.Util import make_numeric_comparison

class SPECjvm2008Comparator(ResultAggregator):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()

    def update(self, measurement):
        comparison = dict()
        for benchmark, score in measurement.items():
            if benchmark not in self._baseline:
                continue
            baseline_score = self._baseline[benchmark]
            comparison[benchmark] = make_numeric_comparison(baseline_score, score)
        self._data.append(comparison)
    
    def get_result(self):
        return self._data
