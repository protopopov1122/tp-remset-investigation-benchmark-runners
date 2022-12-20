#!/usr/bin/env python3
import sys
import traceback
import zipfile
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from typing import List
from collections import namedtuple
from io import BytesIO
from loaders import *
from matplotlib.ticker import AutoMinorLocator
from dataclasses import dataclass

@dataclass
class BenchmarkRun:
    name: str
    data_frame: pandas.DataFrame

@dataclass
class BenchmarkRunLocator:
    name: str
    locations: List[str]

def eval_comparison(baseline: BenchmarkRun, benchmark_run_set: List[BenchmarkRun], pandas_index: List[str], reverse_delta_sign: bool = False) -> pandas.DataFrame:
    data_frames = list()
    for benchmark_run in benchmark_run_set:
        benchmark_run.data_frame['BenchmarkRunID'] = benchmark_run.name
        data_frames.append(benchmark_run.data_frame)

    df = pandas.concat(data_frames)
    df = df.pivot_table(index=pandas_index, columns=['BenchmarkRunID'], values=['Mean', '5th Percentile', '95th Percentile']).swaplevel(axis='columns')
    df.sort_index(axis=1, inplace=True)
    divisor = df[(baseline.name, 'Mean')]
    benchmark_names, value_columns = df.columns.levels
    for benchmark_name in benchmark_names:
        for value_column in value_columns:
            key = (benchmark_name, value_column)
            df[key] = df[key] / divisor
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

def plot_results(data_frame: pandas.DataFrame, title: str, figsize=None):
    benchmark_names, _ = data_frame.columns.levels
    labels = list()
    bar_groups = dict()
    y_range = (math.inf, 0)
    for index, row in data_frame.iterrows():
        labels.append(str(index))
        for benchmark_name in benchmark_names:
            bar_data = (str(index), row[(benchmark_name, 'Mean')], row[(benchmark_name, '5th Percentile')], row[(benchmark_name, '95th Percentile')])
            if benchmark_name not in bar_groups:
                bar_groups[benchmark_name] = list()
            bar_groups[benchmark_name].append(bar_data)
            y_range = (
                min(y_range[0], bar_data[2]),
                max(y_range[1], bar_data[3])
            )
    
    fig = plt.figure(figsize=figsize or (25, 10))
    ax = fig.add_subplot()
    x = np.arange(len(labels))
    group_width = 1.0 / len(labels)
    bar_width = 0.5 / len(bar_groups)
    bar_offset = -0.25
    for bar_label, bars in bar_groups.items():
        bar_values = [
            mean
            for _, mean, _, _ in bars
        ]
        bar_error_min = [
            mean - err
            for _, mean, err, _ in bars
        ]
        bar_error_max = [
            err - mean
            for _, mean, _, err in bars
        ]
        ax.bar(x + bar_offset, bar_values, bar_width, label=bar_label, yerr=[bar_error_min, bar_error_max], capsize=3, error_kw={
            'elinewidth': 0.5,
            'capthick': 0.5
        })
        bar_offset += bar_width
    ax.axhline(y=1.0, color='b', linestyle='-', label='Baseline')
    
    ax.set_title(title)
    ax.set_ylabel('Relative mean')
    ax.set_xticks(x, labels)
    ax.set_xlabel('Benchmark')
    ax.set_ylim(y_range[0] * 0.9, y_range[1] * 1.1)
    ax.legend(bbox_to_anchor = (0.5, -0.2), loc='upper center')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.grid(True, which='major', linestyle='solid')
    ax.yaxis.grid(True, which='minor', linestyle='dotted')

    content = BytesIO()
    fig.tight_layout()
    fig.savefig(content, bbox_inches='tight', dpi=300, format='png')
    return content.getvalue()

def run(args: List[str]):
    archive_output = args[1]
    benchmark_run_sets = locate_benchmark_runs(args[2:])
    baseline_benchmark_runs = benchmark_run_sets[0]

    compiler_speed = compare_compiler_speed(baseline_benchmark_runs, benchmark_run_sets)
    dacapo = compare_dacapo(baseline_benchmark_runs, benchmark_run_sets, 'dacapo')
    dacapo_large = compare_dacapo(baseline_benchmark_runs, benchmark_run_sets, 'dacapo_large')
    dacapo_huge = compare_dacapo(baseline_benchmark_runs, benchmark_run_sets, 'dacapo_huge')
    delay_inducer = compare_delay_inducer(baseline_benchmark_runs, benchmark_run_sets)
    jbb2005 = compare_jbb2005(baseline_benchmark_runs, benchmark_run_sets)
    optaplanner = compare_optaplanner(baseline_benchmark_runs, benchmark_run_sets)
    pjbb2005_msec, pjbb2005_throughput = compare_pjbb2005(baseline_benchmark_runs, benchmark_run_sets)
    renaissance = compare_renaissance(baseline_benchmark_runs, benchmark_run_sets)
    rubykon = compare_rubykon(baseline_benchmark_runs, benchmark_run_sets)
    specjvm2008 = compare_specjvm2008(baseline_benchmark_runs, benchmark_run_sets)

    compiler_speed_plot = plot_results(compiler_speed, 'CompilerSpeed [compiles/sec]')
    dacapo_plot = plot_results(dacapo, 'DaCapo [msec]')
    dacapo_large_plot = plot_results(dacapo_large, 'DaCapo Large [msec]')
    dacapo_huge_plot = plot_results(dacapo_huge, 'DaCapo Huge [msec]')
    delay_inducer_plot = plot_results(delay_inducer, 'DelayInducer [msec]')
    jbb2005_plot = plot_results(jbb2005, 'jbb2005 [throughput]')
    optaplanner_plot = plot_results(optaplanner, 'Optaplanner [score]')
    pjbb2005_msec_plot = plot_results(pjbb2005_msec, 'pjbb2005 [msec]')
    pjbb2005_throughput_plot = plot_results(pjbb2005_throughput, 'pjbb2005 [throughput]')
    renaissance_plot = plot_results(renaissance, 'Renaissance [msec]')
    rubykon_plot = plot_results(rubykon, 'Rubykon [performance]')
    specjvm2008_plot = plot_results(specjvm2008, 'specjvm2008 [ops/m]', figsize=(50, 10))

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