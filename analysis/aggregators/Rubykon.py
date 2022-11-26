import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.Rubykon import Rubykon

class RubykonAggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        super().__init__()
        self._result = dict()

    def update(self, arg: Rubykon):
        for (_, size, iterations), performance in arg.get_results().items():
            self._update_result((size, iterations), performance)
    
    def get_result(self):
        return {
            key: result.get_result()
            for key, result in self._result.items()
        }

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Size', 'Iterations', 'Avg. performance', 'Count', 'Min. performance', 'Max. performance'])
        for (size, iterations), performance in result.items():
            writer.writerow([size, iterations,
                round(performance.average, ResultExporter.get_rounding()),
                performance.sample_count,
                round(performance.minimum, ResultExporter.get_rounding()),
                round(performance.maximum, ResultExporter.get_rounding())])

    
    def _update_result(self, key, performance):
        if key not in self._result:
            self._result[key] = NumericAggregator()
        self._result[key].update(performance)
