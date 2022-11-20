from abc import ABC, abstractmethod
from collections import namedtuple

class ResultAggregator(ABC):
    @abstractmethod
    def update(self, arg): pass

    @abstractmethod
    def get_result(self): pass

class ResultExporter(ABC):
    @abstractmethod
    def export_result(self, destination): pass

class AverageAggregator(ResultAggregator):
    def __init__(self):
        self._value = None
        self._count = 0

    def update(self, arg):
        if self._value is None:
            self._value = arg
        else:
            self._value += arg
        self._count += 1
    
    def get_result(self):
        if self._value is not None:
            if self._count > 1:
                return self._value / self._count
            else:
                return self._value
        else:
            return None

    def get_count(self):
        return self._count

class MinAggregator(ResultAggregator):
    def __init__(self):
        self._value = None

    def update(self, arg):
        if self._value is None:
            self._value = arg
        else:
            self._value = min(self._value, arg)

    def get_result(self):
        return self._value

class MaxAggregator(ResultAggregator):
    def __init__(self):
        self._value = None

    def update(self, arg):
        if self._value is None:
            self._value = arg
        else:
            self._value = max(self._value, arg)

    def get_result(self):
        return self._value

NumericAggregation = namedtuple('NumericAggregation', [
    'average',
    'sample_count',
    'maximum',
    'minimum'
])

class NumericAggregator(ResultAggregator):
    def __init__(self):
        super().__init__()
        self._avg = AverageAggregator()
        self._min = MinAggregator()
        self._max = MaxAggregator()

    def update(self, arg):
        self._avg.update(arg)
        self._min.update(arg)
        self._max.update(arg)

    def get_result(self) -> NumericAggregation:
        return NumericAggregation(
            average=self._avg.get_result(),
            sample_count=self._avg.get_count(),
            minimum=self._min.get_result(),
            maximum=self._max.get_result()
        )
