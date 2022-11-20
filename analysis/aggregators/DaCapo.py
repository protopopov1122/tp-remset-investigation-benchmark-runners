import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.DaCapo import DaCapo

class DaCapoAggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        super().__init__()
        self._result = dict()

    def update(self, arg: DaCapo):
        for name, result in arg.get_results().items():
            self._update_result(name, result)
    
    def get_result(self):
        return {
            name: result.get_result()
            for name, result in self._result.items()
        }

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Benchmark', 'Avg. score', 'Count', 'Min. score', 'Max. score'])
        for name, score in result.items():
            writer.writerow([name,
                round(score.average, 3),
                score.sample_count,
                round(score.minimum, 3),
                round(score.maximum, 3)])

    
    def _update_result(self, name, result):
        if name not in self._result:
            self._result[name] = NumericAggregator()
        self._result[name].update(result)
