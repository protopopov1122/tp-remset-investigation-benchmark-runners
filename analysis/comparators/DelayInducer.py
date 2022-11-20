from aggregators.Util import ResultAggregator
from comparators.Util import make_numeric_comparison

class DelayInducerComparator(ResultAggregator):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()

    def update(self, measurement):
        self._data.append(make_numeric_comparison(self._baseline, measurement, reverse_order=True))
    
    def get_result(self):
        return self._data
