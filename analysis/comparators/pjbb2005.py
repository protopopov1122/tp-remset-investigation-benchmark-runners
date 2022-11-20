from aggregators.Util import ResultAggregator
from comparators.Util import make_numeric_comparison

class pjbb2005Comparator(ResultAggregator):
    def __init__(self, baseline) -> None:
        super().__init__()
        self._baseline = baseline
        self._time = list()
        self._throughput = list()

    def update(self, measurement):
        time_measurement, throughput_measurement = measurement['time'], measurement['throughputs']
        baseline_time, baseline_throughputs = self._baseline['time'], self._baseline['throughputs']
        self._time.append(make_numeric_comparison(baseline_time, time_measurement, reverse_order=True))
        throughput_comparison = dict()
        for warehouses, throughput in throughput_measurement.items():
            if warehouses not in baseline_throughputs:
                continue
            baseline_throughput = baseline_throughputs[warehouses]
            throughput_comparison[warehouses] = make_numeric_comparison(baseline_throughput, throughput)
        self._throughput.append(throughput_comparison)
    
    def get_result(self):
        return {
            'time': self._time,
            'throughputs': self._throughput
        }
