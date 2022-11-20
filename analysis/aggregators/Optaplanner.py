import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.Optaplanner import Optaplanner

class OptaplannerAggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        super().__init__()
        self._result = dict()

    def update(self, arg: Optaplanner):
        for key, score in arg.get_results().items():
            self._update_result(key, score)
    
    def get_result(self):
        return {
            key: score.get_result()
            for key, score in self._result.items()
        }

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['GC', 'Solver ID', 'Avg. score', 'Count', 'Min. score', 'Max. score'])
        for (gc, solverId), score in result.items():
            writer.writerow([gc, solverId,
                round(score['avg'], 3),
                score['count'],
                round(score['min'], 3),
                round(score['max'], 3)])

    
    def _update_result(self, key, score):
        if key not in self._result:
            self._result[key] = NumericAggregator()
        self._result[key].update(score)
