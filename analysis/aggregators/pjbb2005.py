import csv
from aggregators.Util import ResultAggregator, NumericAggregator, ResultExporter
from benchmarks.pjbb2005 import pjbb2005

class pjbb2005Aggregator(ResultAggregator, ResultExporter):
    def __init__(self):
        self._time = NumericAggregator()
        self._throughputs = dict()

    def update(self, arg: pjbb2005):
        run_time, throughputs = arg.get_results()
        for t in run_time:
            self._time.update(t)
        for warehouses, result in throughputs.items():
            self._update_result(warehouses, result)
    
    def get_result(self):
        return {
            'time': self._time.get_result(),
            'throughputs': {
                warehouses: result.get_result()
                for warehouses, result in self._throughputs.items()
            }
        }

    def export_result(self, destination, throughputs: bool=True):
        result = self.get_result()
        writer = csv.writer(destination)
        if not throughputs:
            writer.writerow(['Avg. time', 'Count', 'Min. time', 'Max. time'])
            time_result = result['time']
            writer.writerow([
                round(time_result.average, ResultExporter.get_rounding()),
                time_result.sample_count,
                round(time_result.minimum, ResultExporter.get_rounding()),
                round(time_result.maximum, ResultExporter.get_rounding())])
        else:
            writer.writerow(['Warehouses', 'Avg. score', 'Count', 'Min. score', 'Max. score'])
            for warehouses, throughput in result['throughputs'].items():
                writer.writerow([warehouses,
                    round(throughput.average, ResultExporter.get_rounding()),
                    throughput.sample_count,
                    round(throughput.minimum, ResultExporter.get_rounding()),
                    round(throughput.maximum, ResultExporter.get_rounding())])
    
    def _update_result(self, warehouses, result):
        if warehouses not in self._throughputs:
            self._throughputs[warehouses] = NumericAggregator()
        self._throughputs[warehouses].update(result)
