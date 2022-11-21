import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class DelayInducerComparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._data = list()
        self.update(self._baseline)

    def update(self, measurement):
        self._data.append({
            'value': measurement,
            'delta': make_numeric_comparison(self._baseline, measurement, reverse_order=True)
        })
    
    def get_result(self):
        return self._data

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Run', 'Average', 'Absolute change', 'Relative change'])
        for index, msec_comparison in enumerate(result):
            delta = msec_comparison['delta']
            writer.writerow([index,
                round(msec_comparison['value'].average, 3),
                round(delta.absolute_delta, 3),
                round(delta.relative_delta, 3)])
