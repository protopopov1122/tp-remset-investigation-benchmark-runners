import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.Renaissance import Renaissance

class RenaissainceAggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        self._result = dict()

    def update(self, arg: Renaissance):
        for name, results in arg.get_results().items():
            for result in results:
                self._update_result(name, result['duration'])
    
    def get_result(self):
        return {
            name: result.get_result()
            for name, result in self._result.items()
        }

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Benchmark', 'Avg. duration', 'Count', 'Min. duration', 'Max. duration'])
        for name, score in result.items():
            writer.writerow([name,
                round(score.average, 3),
                score.sample_count,
                round(score.minimum, 3),
                round(score.maximum, 3)])
    
    def _update_result(self, name, duration):
        if name not in self._result:
            self._result[name] = NumericAggregator()
        self._result[name].update(duration)
