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
        delay = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Average', 'Count', 'Minimum', 'Maximum'])
        writer.writerow([
            round(delay.average, ResultExporter.get_rounding()),
            delay.sample_count,
            round(delay.minimum, ResultExporter.get_rounding()),
            round(delay.maximum, ResultExporter.get_rounding())])
    
    def get_result(self):
        return self._result.get_result()
