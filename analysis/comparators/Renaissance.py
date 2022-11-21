import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class RenaissanceComparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for benchmark, duration in measurement.items():
            if benchmark not in self._baseline:
                continue
            baseline_duration = self._baseline[benchmark]
            comparison[benchmark] = {
                'value': duration,
                'delta': make_numeric_comparison(baseline_duration, duration, reverse_order=True)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Benchmark', 'Average', 'Absolute change', 'Relative change'])
        for index, comparison in enumerate(result):
            for name, duration_comparison in comparison.items():
                delta = duration_comparison['delta']
                writer.writerow([index, name,
                    round(duration_comparison['value'].average, ResultExporter.get_rounding()),
                    round(delta.absolute_delta, ResultExporter.get_rounding()),
                    round(delta.relative_delta, ResultExporter.get_rounding())])