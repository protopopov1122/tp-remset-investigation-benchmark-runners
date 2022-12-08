#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path
from typing import List
import zipfile
from loaders import *

def eval_comparison(baseline: pandas.DataFrame, comparison: pandas.DataFrame, index: List[str], reverse_order: bool = False) -> pandas.DataFrame:
    baseline['Benchmark Run'] = 'baseline'
    comparison['Benchmark Run'] = 'comparison'
    df = pandas.concat([baseline, comparison])
    df = df.pivot_table(index=index, columns=['Benchmark Run'], values=['Mean'])
    df = df.sort_index(axis='columns', level='Benchmark Run')
    df.columns = ['Baseline mean', 'Comparison mean']
    df['Delta'] =  df['Comparison mean'] - df['Baseline mean'] if not reverse_order else df['Baseline mean'] - df['Comparison mean']
    df['Relative'] = df['Delta'] / df['Baseline mean']
    return df

def compare_compiler_speed(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_compiler_speed(baseline_benchmark_runs)
    comparison = load_compiler_speed(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['Time limit', 'Threads'])

def compare_dacapo(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path], name: str):
    baseline = load_dacapo(baseline_benchmark_runs, name)
    comparison = load_dacapo(comparison_benchmark_runs, name)
    return eval_comparison(baseline, comparison, ['Benchmark'], True)

def compare_delay_inducer(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_delay_inducer(baseline_benchmark_runs)
    comparison = load_delay_inducer(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['index'], True)

def compare_jbb2005(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_jbb2005(baseline_benchmark_runs)
    comparison = load_jbb2005(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['warehouses'])

def compare_optaplanner(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_optaplanner(baseline_benchmark_runs)
    comparison = load_optaplanner(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['solverId'])

def compare_pjbb2005(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline_msec, baseline_throughput = load_pjbb2005(baseline_benchmark_runs)
    comparison_msec, comparison_throughput = load_pjbb2005(comparison_benchmark_runs)
    return eval_comparison(baseline_msec, comparison_msec, ['Operation'], True), \
           eval_comparison(baseline_throughput, comparison_throughput, ['warehouses'])

def compare_renaissance(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_renaissance(baseline_benchmark_runs)
    comparison = load_renaissance(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['benchmark'], True)

def compare_rubykon(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_rubykon(baseline_benchmark_runs)
    comparison = load_rubykon(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['Size', 'Iterations'])

def compare_specjvm2008(baseline_benchmark_runs: List[Path], comparison_benchmark_runs: List[Path]):
    baseline = load_specjvm2008(baseline_benchmark_runs)
    comparison = load_specjvm2008(comparison_benchmark_runs)
    return eval_comparison(baseline, comparison, ['Benchmark'])

def run(args: List[str]):
    archive_output = args[1]
    separator_idx = args.index('--')
    baseline_benchmark_runs = [Path(arg) for arg in args[2:separator_idx]]
    comparison_benchmark_runs = [Path(arg) for arg in args[separator_idx + 1:]]

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
