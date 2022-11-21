import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class OptaplannerComparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for key, score in measurement.items():
            if key not in self._baseline:
                continue
            baseline_score = self._baseline[key]
            comparison[key] = {
                'value': score,
                'delta': make_numeric_comparison(baseline_score, score)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'GC', 'Solver ID', 'Average', 'Absolute change', 'Relative change'])
        for index, comparison in enumerate(result):
            for (gc, solverId), score_comparison in comparison.items():
                delta = score_comparison['delta']
                writer.writerow([index, gc, solverId,
                    round(score_comparison['value'].average, ResultExporter.get_rounding()),
                    round(delta.absolute_delta, ResultExporter.get_rounding()),
                    round(delta.relative_delta, ResultExporter.get_rounding())])
