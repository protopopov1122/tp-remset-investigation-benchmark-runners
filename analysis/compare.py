#!/usr/bin/env python3
import sys
import os
import traceback
from pathlib import Path
from typing import List, Tuple, Optional
import zipfile
from collections import namedtuple
from loaders import *

BenchmarkRuns = namedtuple('BenchmarkRuns', ['name', 'data_frame'])

def eval_comparison(baseline: BenchmarkRuns, comparison: List[BenchmarkRuns], pandas_index: List[str], reverse_delta_sign: bool = False) -> pandas.DataFrame:
    data_frames = [baseline.data_frame]
    baseline.data_frame['ComparisonID'] = baseline.name
    for benchmark_runs in comparison:
        benchmark_runs.data_frame['ComparisonID'] = benchmark_runs.name
        data_frames.append(benchmark_runs.data_frame)

    df = pandas.concat(data_frames)
    df = df.pivot_table(index=pandas_index, columns=['ComparisonID'], values=['Mean'])
    column_names = [benchmark_runs.name for benchmark_runs in comparison]
    column_names.append(baseline.name)
    df = df.sort_index(axis='columns', level='ComparisonID')
    df.columns = sorted(column_names)
    for benchmark_runs in comparison:
        if reverse_delta_sign:
            delta_key = f'Delta({baseline.name}, {benchmark_runs.name})'
            rel_key = f'Relative({baseline.name}, {benchmark_runs.name})'
            df[delta_key] = df[baseline.name] - df[benchmark_runs.name]
        else:
            delta_key = f'Delta({benchmark_runs.name}, {baseline.name})'
            rel_key = f'Relative({benchmark_runs.name}, {baseline.name})'
            df[delta_key] = df[benchmark_runs.name] - df[baseline.name]
        df[rel_key] = df[delta_key] / df[baseline.name]
    return df

def compare_compiler_speed(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_compiler_speed(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_compiler_speed(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['Time limit', 'Threads'])

def compare_dacapo(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]], bench_name: str):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_dacapo(baseline_benchmark_runs[1], bench_name))
    comparison = [BenchmarkRuns(name, load_dacapo(comparison_benchmark_runs, bench_name)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['Benchmark'], True)

def compare_delay_inducer(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_delay_inducer(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_delay_inducer(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['Benchmark'], True)

def compare_jbb2005(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_jbb2005(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_jbb2005(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['warehouses'])

def compare_optaplanner(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_optaplanner(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_optaplanner(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['solverId'])

def compare_pjbb2005(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline_msec = BenchmarkRuns(baseline_benchmark_runs[0], load_pjbb2005_msec(baseline_benchmark_runs[1]))
    comparison_msec = [BenchmarkRuns(name, load_pjbb2005_msec(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    baseline_throughput = BenchmarkRuns(baseline_benchmark_runs[0], load_pjbb2005_throughput(baseline_benchmark_runs[1]))
    comparison_throughput = [BenchmarkRuns(name, load_pjbb2005_throughput(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline_msec, comparison_msec, ['Operation'], True), \
           eval_comparison(baseline_throughput, comparison_throughput, ['warehouses'])

def compare_renaissance(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_renaissance(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_renaissance(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['benchmark'], True)

def compare_rubykon(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_rubykon(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_rubykon(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['Size', 'Iterations'])

def compare_specjvm2008(baseline_benchmark_runs: Tuple[str, List[Path]], comparison_benchmark_run_sets: List[Tuple[str, List[Path]]]):
    baseline = BenchmarkRuns(baseline_benchmark_runs[0], load_specjvm2008(baseline_benchmark_runs[1]))
    comparison = [BenchmarkRuns(name, load_specjvm2008(comparison_benchmark_runs)) for name, comparison_benchmark_runs in comparison_benchmark_run_sets]
    return eval_comparison(baseline, comparison, ['Benchmark'])

def interpret_args(args: List[str]) -> List[Tuple[str, List[Path]]]:
    result = list()
    while args:
        name = args[0]
        try:
            dir_list_terminator = args.index(';')
        except:
            dir_list_terminator = None
        
        if dir_list_terminator:
            dir_list = args[1:dir_list_terminator]
            args = args[dir_list_terminator + 1:]
        else:
            dir_list = args[1:]
            args = None
        result.append((name, [Path(d) for d in dir_list]))
    return result

def run(args: List[str]):
    archive_output = args[1]
    benchmark_run_sets = interpret_args(args[2:])
    baseline_benchmark_runs = benchmark_run_sets[0]
    comparison_benchmark_runs = benchmark_run_sets[1:]

    compiler_speed = compare_compiler_speed(baseline_benchmark_runs, comparison_benchmark_runs)
    dacapo = compare_dacapo(baseline_benchmark_runs, comparison_benchmark_runs, 'dacapo')
    dacapo_large = compare_dacapo(baseline_benchmark_runs, comparison_benchmark_runs, 'dacapo_large')
    dacapo_huge = compare_dacapo(baseline_benchmark_runs, comparison_benchmark_runs, 'dacapo_huge')
    delay_inducer = compare_delay_inducer(baseline_benchmark_runs, comparison_benchmark_runs)
    jbb2005 = compare_jbb2005(baseline_benchmark_runs, comparison_benchmark_runs)
    optaplanner = compare_optaplanner(baseline_benchmark_runs, comparison_benchmark_runs)
    pjbb2005_msec, pjbb2005_throughput = compare_pjbb2005(baseline_benchmark_runs, comparison_benchmark_runs)
    renaissance = compare_renaissance(baseline_benchmark_runs, comparison_benchmark_runs)
    rubykon = compare_rubykon(baseline_benchmark_runs, comparison_benchmark_runs)
    specjvm2008 = compare_specjvm2008(baseline_benchmark_runs, comparison_benchmark_runs)

    with zipfile.ZipFile(archive_output, 'w') as archive:
        archive.writestr('CompilerSpeed.csv', compiler_speed.to_csv())
        archive.writestr('DaCapo.csv', dacapo.to_csv())
        archive.writestr('DaCapo_large.csv', dacapo_large.to_csv())
        archive.writestr('DaCapo_huge.csv', dacapo_huge.to_csv())
        archive.writestr('DelayInducer.csv', delay_inducer.to_csv())
        archive.writestr('jbb2005.csv', jbb2005.to_csv())
        archive.writestr('Optaplanner.csv', optaplanner.to_csv())
        archive.writestr('pjbb2005_msec.csv', pjbb2005_msec.to_csv())
        archive.writestr('pjbb2005_throughput.csv', pjbb2005_throughput.to_csv())
        archive.writestr('Renaissance.csv', renaissance.to_csv())
        archive.writestr('Rubykon.csv', rubykon.to_csv())
        archive.writestr('specjvm2008.csv', specjvm2008.to_csv())

if __name__ == '__main__':
    try:
        run(sys.argv)
    except:
        traceback.print_exc()
        sys.exit(-1)
