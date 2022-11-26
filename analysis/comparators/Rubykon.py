import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class RubykonComparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for key, performance in measurement.items():
            if key not in self._baseline:
                continue
            baseline_peformance = self._baseline[key]
            comparison[key] = {
                'value': performance,
                'delta': make_numeric_comparison(baseline_peformance, performance)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Size', 'Iterations', 'Average', 'Absolute change', 'Relative change'])
        for index, performance_comparisons in enumerate(result):
            for (size, iterations), performance in performance_comparisons.items():
                delta = performance['delta']
                writer.writerow([index, size, iterations,
                    round(performance['value'].average, ResultExporter.get_rounding()),
                    round(delta.absolute_delta, ResultExporter.get_rounding()),
                    round(delta.relative_delta, ResultExporter.get_rounding())])
