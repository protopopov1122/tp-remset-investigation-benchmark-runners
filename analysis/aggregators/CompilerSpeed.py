import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.CompilerSpeed import CompilerSpeed

class CompilerSpeedAggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        super().__init__()
        self._result = dict()

    def update(self, arg: CompilerSpeed):
        for duration, measurements in arg.get_results().items():
            for measurement in measurements:
                self._update_result(duration, measurement)
    
    def get_result(self):
        return {
            duration: aggregator.get_result()
            for duration, aggregator in self._result.items()
        }

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Duration', 'Average', 'Count', 'Minimum', 'Maximum'])
        for duration, ops_per_sec in result.items():
            writer.writerow([duration,
                round(ops_per_sec.average, 3),
                ops_per_sec.sample_count,
                round(ops_per_sec.minimum, 3),
                round(ops_per_sec.maximum, 3)])

    
    def _update_result(self, duration, measurement):
        if duration not in self._result:
            self._result[duration] = NumericAggregator()
        self._result[duration].update(measurement)
