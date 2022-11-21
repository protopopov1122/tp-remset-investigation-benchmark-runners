import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class SPECjbb2005Comparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        comparison = dict()
        for warehouses, score in measurement.items():
            if warehouses not in self._baseline:
                continue
            baseline_score = self._baseline[warehouses]
            comparison[warehouses] = {
                'value': score,
                'delta': make_numeric_comparison(baseline_score, score)
            }
        self._data.append(comparison)
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Warehouses', 'Average', 'Absolute change', 'Relative change'])
        for index, msec_comparisons in enumerate(result):
            for warehouses, msec_comparison in msec_comparisons.items():
                delta = msec_comparison['delta']
                writer.writerow([index, warehouses,
                    round(msec_comparison['value'].average, ResultExporter.get_rounding()),
                    round(delta.absolute_delta, ResultExporter.get_rounding()),
                    round(delta.relative_delta, ResultExporter.get_rounding())])
