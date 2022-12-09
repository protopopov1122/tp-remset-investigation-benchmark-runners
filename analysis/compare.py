#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path
from typing import List
import zipfile
from collections import namedtuple
from io import BytesIO
from loaders import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np

BenchmarkRun = namedtuple('BenchmarkRun', ['name', 'data_frame'])
BenchmarkRunLocator = namedtuple('BenchmarkRunLocator', ['name', 'locations'])

def delta_column_name(baseline_name: str, run_name: str, reverse: bool) -> str:
    if reverse:
        return f'Delta({baseline_name}, {run_name})'
    else:
        return f'Delta({run_name}, {baseline_name})'

def relative_column_name(baseline_name: str, run_name: str, reverse: bool) -> str:
    if reverse:
        return f'Relative({baseline_name}, {run_name})'
    else:
        return f'Relative({run_name}, {baseline_name})'

def eval_comparison(baseline: BenchmarkRun, comparison: List[BenchmarkRun], pandas_index: List[str], reverse_delta_sign: bool = False) -> pandas.DataFrame:
    data_frames = [baseline.data_frame]
    column_names = [baseline.name]
    baseline.data_frame['BenchmarkRunID'] = baseline.name
    for benchmark_run in comparison:
        benchmark_run.data_frame['BenchmarkRunID'] = benchmark_run.name
        data_frames.append(benchmark_run.data_frame)
        column_names.append(benchmark_run.name)

    df = pandas.concat(data_frames)
    df = df.pivot_table(index=pandas_index, columns=['BenchmarkRunID'], values=['Mean'])
    df = df.sort_index(axis='columns', level='BenchmarkRunID')
    df.columns = sorted(column_names)
    for benchmark_run in comparison:
        delta_key = delta_column_name(baseline.name, benchmark_run.name, reverse_delta_sign)
        rel_key = relative_column_name(baseline.name, benchmark_run.name, reverse_delta_sign)
        if reverse_delta_sign:
            df[delta_key] = df[baseline.name] - df[benchmark_run.name]
        else:
            df[delta_key] = df[benchmark_run.name] - df[baseline.name]
        df[rel_key] = df[delta_key] / df[baseline.name]
    return df

def compare_compiler_speed(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_compiler_speed(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_compiler_speed(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['Time limit', 'Threads'])

def compare_dacapo(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator], bench_name: str):
    baseline = BenchmarkRun(baseline_locator.name, load_dacapo(baseline_locator.locations, bench_name))
    comparison = [
        BenchmarkRun(locator.name, load_dacapo(locator.locations, bench_name))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['Benchmark'], True)

def compare_delay_inducer(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_delay_inducer(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_delay_inducer(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['Benchmark'], True)

def compare_jbb2005(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_jbb2005(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_jbb2005(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['warehouses'])

def compare_optaplanner(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_optaplanner(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_optaplanner(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['solverId'])

def compare_pjbb2005(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline_msec = BenchmarkRun(baseline_locator.name, load_pjbb2005_msec(baseline_locator.locations))
    baseline_throughput = BenchmarkRun(baseline_locator.name, load_pjbb2005_throughput(baseline_locator.locations))
    comparison_msec = [
        BenchmarkRun(locator.name, load_pjbb2005_msec(locator.locations))
        for locator in comparison_locators
    ]
    comparison_throughput = [
        BenchmarkRun(locator.name, load_pjbb2005_throughput(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline_msec, comparison_msec, ['Operation'], True), \
           eval_comparison(baseline_throughput, comparison_throughput, ['warehouses'])

def compare_renaissance(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_renaissance(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_renaissance(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['benchmark'], True)

def compare_rubykon(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_rubykon(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_rubykon(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['Size', 'Iterations'])

def compare_specjvm2008(baseline_locator: BenchmarkRunLocator, comparison_locators: List[BenchmarkRunLocator]):
    baseline = BenchmarkRun(baseline_locator.name, load_specjvm2008(baseline_locator.locations))
    comparison = [
        BenchmarkRun(locator.name, load_specjvm2008(locator.locations))
        for locator in comparison_locators
    ]
    return eval_comparison(baseline, comparison, ['Benchmark'])

def locate_benchmark_runs(args: List[str]) -> List[BenchmarkRunLocator]:
    result = list()
    while args:
        name = args[0]
        try:
            dir_list_terminator = args.index(';')
        except ValueError:
            dir_list_terminator = None
        
        if dir_list_terminator:
            dir_list = args[1:dir_list_terminator]
            args = args[dir_list_terminator + 1:]
        else:
            dir_list = args[1:]
            args = None
        result.append(BenchmarkRunLocator(name, [Path(d) for d in dir_list]))
    return result

def plot_relative_results(data_frame: pandas.DataFrame, title: str, figsize=None):
    labels = list()
    values = dict()
    for index, row in data_frame.iterrows():
        labels.append(str(index))
        for rel_name, value in row.items():
            if 'Relative' in rel_name:
                if rel_name not in values:
                    values[rel_name] = list()
                values[rel_name].append(value)
    
    fig = plt.figure(figsize=figsize or (25, 10))
    ax = fig.add_subplot()
    x = np.arange(len(labels))
    group_width = 1.0 / len(labels)
    bar_width = 0.5 / len(values)
    bar_offset = -group_width / 2
    for rel_name, values in values.items():
        ax.bar(x + bar_offset, values, bar_width, label=rel_name)
        bar_offset += bar_width
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07))
    ax.set_xticks(x, labels)
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.grid(True, which='major', linestyle='solid')
    ax.yaxis.grid(True, which='minor', linestyle='dotted')
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('Improvement over baseline')
    ax.set_title(title)
    content = BytesIO()
    fig.tight_layout()
    fig.savefig(content, bbox_inches='tight', dpi=300, format='png')
    return content.getvalue()

def run(args: List[str]):
    archive_output = args[1]
    benchmark_run_sets = locate_benchmark_runs(args[2:])
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

    compiler_speed_plot = plot_relative_results(compiler_speed, 'CompilerSpeed')
    dacapo_plot = plot_relative_results(dacapo, 'DaCapo')
    dacapo_large_plot = plot_relative_results(dacapo_large, 'DaCapo Large')
    dacapo_huge_plot = plot_relative_results(dacapo_huge, 'DaCapo Huge', figsize=(10, 10))
    delay_inducer_plot = plot_relative_results(delay_inducer, 'DelayInducer', figsize=(10, 10))
    jbb2005_plot = plot_relative_results(jbb2005, 'jbb2005')
    optaplanner_plot = plot_relative_results(optaplanner, 'Optaplanner')
    pjbb2005_msec_plot = plot_relative_results(pjbb2005_msec, 'pjbb2005 (msec)')
    pjbb2005_throughput_plot = plot_relative_results(pjbb2005_throughput, 'pjbb2005 (throughput)')
    renaissance_plot = plot_relative_results(renaissance, 'Renaissance')
    rubykon_plot = plot_relative_results(rubykon, 'Rubykon', figsize=(10, 10))
    specjvm2008_plot = plot_relative_results(specjvm2008, 'specjvm2008', figsize=(50, 10))

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

        archive.writestr('plots/CompilerSpeed.png', compiler_speed_plot)
        archive.writestr('plots/DaCapo.png', dacapo_plot)
        archive.writestr('plots/DaCapo_large.png', dacapo_large_plot)
        archive.writestr('plots/DaCapo_huge.png', dacapo_huge_plot)
        archive.writestr('plots/DelayInducer.png', delay_inducer_plot)
        archive.writestr('plots/jbb2005.png', jbb2005_plot)
        archive.writestr('plots/Optaplanner.png', optaplanner_plot)
        archive.writestr('plots/pjbb2005_msec.png', pjbb2005_msec_plot)
        archive.writestr('plots/pjbb2005_throughput.png', pjbb2005_throughput_plot)
        archive.writestr('plots/renaissance.png', renaissance_plot)
        archive.writestr('plots/rubykon.png', rubykon_plot)
        archive.writestr('plots/specjvm2008.png', specjvm2008_plot)

if __name__ == '__main__':
    try:
        run(sys.argv)
    except:
        traceback.print_exc()
        sys.exit(-1)
