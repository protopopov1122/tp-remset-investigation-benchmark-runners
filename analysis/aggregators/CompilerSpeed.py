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
        for duration, dur_results in result.items():
            writer.writerow([duration,
                round(dur_results['avg'], 3),
                dur_results['count'],
                round(dur_results['min'], 3),
                round(dur_results['max'], 3)])

    
    def _update_result(self, duration, measurement):
        if duration not in self._result:
            self._result[duration] = NumericAggregator()
        self._result[duration].update(measurement)
