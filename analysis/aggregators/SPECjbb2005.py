import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.SPECjbb2005 import SPECjbb2005

class SPECjbb2005Aggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        self._result = dict()

    def update(self, arg: SPECjbb2005):
        for warehouses, result in arg.get_results().items():
            self._update_result(warehouses, result)
    
    def get_result(self):
        return {
            warehouses: result.get_result()
            for warehouses, result in self._result.items()
        }

    def export_result(self, destination):
        result = self.get_result()
        writer = csv.writer(destination)
        writer.writerow(['Warehouses', 'Avg. score', 'Count', 'Min. score', 'Max. score'])
        for warehouses, throughput in result.items():
            writer.writerow([warehouses,
                round(throughput.average, ResultExporter.get_rounding()),
                throughput.sample_count,
                round(throughput.minimum, ResultExporter.get_rounding()),
                round(throughput.maximum, ResultExporter.get_rounding())])
    
    def _update_result(self, warehouses, result):
        if warehouses not in self._result:
            self._result[warehouses] = NumericAggregator()
        self._result[warehouses].update(result)
