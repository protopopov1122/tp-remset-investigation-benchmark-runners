
from pathlib import Path
from typing import List
import pandas
import os
import math

def q05(x):
    return x.quantile(0.05)

def q95(x):
    return x.quantile(0.95)

AGG_FN = ['mean', 'min', 'max', 'count', 'std', q05, q95]
AGG_COLUMNS = ['Mean', 'Min', 'Max', 'Count', 'Std. Dev', '5th Percentile', '95th Percentile']

def load_csv_frames(benchmark_runs: List[Path], filename: str) -> pandas.DataFrame:
    csv_files = [benchmark_run.joinpath(filename) for benchmark_run in benchmark_runs]
    for csv_file in csv_files:
        if not csv_file.exists():
            raise RuntimeError(f'{csv_file} does not exist!')
    return pandas.concat(pandas.read_csv(csv_file) for csv_file in csv_files)

def load_compiler_speed(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/CompilerSpeed/results.csv')
    df = df.groupby(['Time limit', 'Threads'])[['Compiles/Sec']].agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_dacapo(benchmark_runs: List[Path], name: str) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, f'benchmarks/{name}/results.csv')
    df = df.groupby(['Benchmark'])[['Time (msec)']].agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_delay_inducer(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/DelayInducer/results.csv')
    df['Benchmark'] = 0
    df = df.groupby(['Benchmark']).agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_jbb2005(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/jbb2005/results.csv')
    df = df.groupby(['warehouses']).agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_optaplanner(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/optaplanner/results/summary.csv')
    df = df.groupby(['solverId'])[['scoreCalculationCount']].agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_pjbb2005_msec(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/pjbb2005/results1.csv')
    df = df.groupby(['Operation']).agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_pjbb2005_throughput(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/pjbb2005/results2.csv')
    df = df.groupby(['warehouses']).agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_renaissance(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/renaissance/results.csv')
    df = df[['benchmark', 'duration_ns']]
    drop_outliers = float(os.getenv('RENAISSANCE_DROP_OUTLIERS', default='0'))
    if drop_outliers > 0:
        drop_outliers *= 0.5
        grouping = df.groupby(['benchmark'], as_index=False, group_keys=False)
        min_outliers = grouping.apply(lambda grp: grp.nsmallest(math.floor(drop_outliers * len(grp)), columns='duration_ns'))
        df.drop(min_outliers.index, inplace=True)
        grouping = df.groupby(['benchmark'], as_index=False, group_keys=False)
        max_outliers = grouping.apply(lambda grp: grp.nlargest(math.floor(drop_outliers * len(grp) / (1.0 - drop_outliers)), columns='duration_ns'))
        df.drop(max_outliers.index, inplace=True)
    df = df.groupby(['benchmark']).agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_rubykon(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/rubykon/results.csv')
    df = df.query('Type == "runtime"').groupby(['Size', 'Iterations'])[['Performance']].agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df

def load_specjvm2008(benchmark_runs: List[Path]) -> pandas.DataFrame:
    df = load_csv_frames(benchmark_runs, 'benchmarks/specjvm2008/results.csv')
    df = df.groupby(['Benchmark']).agg(AGG_FN)
    df.columns = AGG_COLUMNS
    return df
