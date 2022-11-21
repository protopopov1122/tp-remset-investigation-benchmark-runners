import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class DaCapoComparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for benchmark, msec in measurement.items():
            if benchmark not in self._baseline:
                continue
            baseline_msec = self._baseline[benchmark]
            comparison[benchmark] = {
                'value': msec,
                'delta': make_numeric_comparison(baseline_msec, msec, reverse_order=True)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Benchmark', 'Average', 'Absolute change', 'Relative change'])
        for index, comparison in enumerate(result):
            for name, msec_comparison in comparison.items():
                delta = msec_comparison['delta']
                writer.writerow([index, name,
                    round(msec_comparison['value'].average, ResultExporter.get_rounding()),
                    round(delta.absolute_delta, ResultExporter.get_rounding()),
                    round(delta.relative_delta, ResultExporter.get_rounding())])
