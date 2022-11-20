import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.DelayInducer import DelayInducer

class DelayInducerAggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        self._result = NumericAggregator()

    def update(self, arg: DelayInducer):
        for measurement in arg.get_results():
            self._result.update(measurement)

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Average', 'Count', 'Minimum', 'Maximum'])
        writer.writerow([
            round(result['avg'], 3),
            result['count'],
            round(result['min'], 3),
            round(result['max'], 3)])
    
    def get_result(self):
        return self._result.get_result()
