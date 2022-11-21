import csv
from aggregators.Util import ResultAggregator, ResultExporter
from comparators.Util import make_numeric_comparison

class pjbb2005Comparator(ResultAggregator, ResultExporter):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._time = list()
        self._throughput = list()
        self.update(self._baseline)

    def update(self, measurement):
        time_measurement, throughput_measurement = measurement['time'], measurement['throughputs']
        baseline_time, baseline_throughputs = self._baseline['time'], self._baseline['throughputs']
        self._time.append({
            'value': time_measurement,
            'delta': make_numeric_comparison(baseline_time, time_measurement, reverse_order=True)
        })
        throughput_comparison = dict()
        for warehouses, throughput in throughput_measurement.items():
            if warehouses not in baseline_throughputs:
                continue
            baseline_throughput = baseline_throughputs[warehouses]
            throughput_comparison[warehouses] = {
                'value': throughput,
                'delta': make_numeric_comparison(baseline_throughput, throughput)
            }
        self._throughput.append(throughput_comparison)
    
    def get_result(self):
        return {
            'time': self._time,
            'throughputs': self._throughput
        }

    def export_result(self, destination, export_throughput: bool = False):
        result = self.get_result()
        writer = csv.writer(destination)
        if export_throughput:
            throughput_comparisons = result['throughputs']
            writer.writerow(['Run', 'Warehouses', 'Average', 'Absolute change', 'Relative change'])
            for index, throughput_comparison in enumerate(throughput_comparisons):
                for warehouses, throughput in throughput_comparison.items():
                    throughput_delta = throughput['delta']
                    writer.writerow([index,
                        warehouses,
                        round(throughput['value'].average, 3),
                        round(throughput_delta.absolute_delta, 3),
                        round(throughput_delta.relative_delta, 3) if throughput_delta.relative_delta is not None else ''])
        else:
            time_comparisons = result['time']
            writer.writerow(['Run', 'Average', 'Absolute change', 'Relative change'])
            for index, time_comparison in enumerate(time_comparisons):
                time_delta = time_comparison['delta']
                writer.writerow([index,
                    round(time_comparison['value'].average, 3),
                    round(time_delta.absolute_delta, 3),
                    round(time_delta.relative_delta, 3)])
