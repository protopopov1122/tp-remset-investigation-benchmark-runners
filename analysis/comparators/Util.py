from collections import namedtuple
from aggregators.Util import NumericAggregation

NumericComparison = namedtuple('NumericComparison', ['absolute_delta', 'relative_delta'])

def make_numeric_comparison(baseline: NumericAggregation, comparable: NumericAggregation, reverse_order: bool = False) -> NumericComparison:
    if not reverse_order:
        delta = comparable.average - baseline.average
    else:
        delta = baseline.average - comparable.average
    try:
        relative_delta = delta / baseline.average
    except ZeroDivisionError as ex:
        relative_delta = None
    return NumericComparison(absolute_delta=delta, relative_delta=relative_delta)
