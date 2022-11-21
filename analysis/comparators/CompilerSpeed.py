import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class CompilerSpeedComparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for duration, ops_per_sec in measurement.items():
            if duration not in self._baseline:
                continue
            baseline_ops_per_sec = self._baseline[duration]
            comparison[duration] = {
                'value': ops_per_sec,
                'delta': make_numeric_comparison(baseline_ops_per_sec, ops_per_sec)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Duration', 'Average', 'Absolute change', 'Relative change'])
        for index, comparison in enumerate(result):
            for duration, ops_comparison in comparison.items():
                delta = ops_comparison['delta']
                writer.writerow([index, duration,
                    round(ops_comparison['value'].average, 3),
                    round(delta.absolute_delta, 3),
                    round(delta.relative_delta, 3)])
