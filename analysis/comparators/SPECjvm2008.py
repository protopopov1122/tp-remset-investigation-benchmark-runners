import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class SPECjvm2008Comparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for benchmark, score in measurement.items():
            if benchmark not in self._baseline:
                continue
            baseline_score = self._baseline[benchmark]
            comparison[benchmark] = {
                'value': score,
                'delta': make_numeric_comparison(baseline_score, score)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Benchmark', 'Average', 'Absolute change', 'Relative change'])
        for index, comparison in enumerate(result):
            for name, score_comparison in comparison.items():
                delta = score_comparison['delta']
                writer.writerow([index, name,
                    round(score_comparison['value'].average, 3),
                    round(delta.absolute_delta, 3),
                    round(delta.relative_delta, 3)])
