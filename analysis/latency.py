#!/usr/bin/env python3
import sys
import os
import traceback
import re
import pandas
import zipfile
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from io import BytesIO
from dataclasses import dataclass
from typing import List
from pathlib import Path
from analyze import locate_benchmark_runs, BenchmarkRunLocator, expand_min_max
from loaders import p05, p95

@dataclass
class GCLatency:
    log_file: Path
    gc_cause: str
    latency: float


AGG_FN = ['mean', 'min', 'max', 'count', 'std', p05, p95]
AGG_COLUMNS = ['Mean', 'Min', 'Max', 'Count', 'Std. Dev', '5th Percentile', '95th Percentile']

LATENCY_FILTER_FULL = os.getenv('LATENCY_FILTER_FULL') == 'yes'
LATENCY_FILTER_SYSTEM_GC = os.getenv('LATENCY_FILTER_SYSTEM_GC') == 'yes'

@dataclass
class BenchmarkLatency:
    benchmark_runs: BenchmarkRunLocator
    name: str
    data_frame: pandas.DataFrame
    
    def aggregate_latencies(self) -> pandas.DataFrame:
        aggregated = self.data_frame[['Latency']].agg(AGG_FN)
        aggregated.columns = [self.name]
        pivot = aggregated.pivot_table(columns=aggregated.index, values=[self.name])
        return pivot

    def aggregate_causes(self) -> pandas.DataFrame:
        causes = self.data_frame[['Cause']]
        causes['count'] = 1
        aggregated = causes.groupby(['Cause']).agg(['sum'])
        aggregated.columns = [self.name]
        pivot = aggregated.pivot_table(columns=aggregated.index, values=[self.name])
        return pivot

@dataclass
class BenchmarkLatencyAggregation:
    latency: pandas.DataFrame
    causes: pandas.DataFrame

class BenchmarkLatencyExtractor:
    LOG_REGEXP_PATTERN = re.compile(r'(Pause.*\(.*\))\s*[0-9]+[a-zA-Z]->[0-9]+[a-zA-Z]\s*\([0-9]+[a-zA-Z]\)\s*([0-9]+(\.[0-9]+)?)ms')

    def __init__(self, benchmark_dir: Path):
        self._dir = benchmark_dir

    def locate_gc_logs(self):
        return list(self._dir.glob("gc_logs/*.log"))

    def extract_latencies(self):
        for log_file in self.locate_gc_logs():
            yield from BenchmarkLatencyExtractor.extract_latencies_from_gc_log(log_file)

    def extract_latencies_from_gc_log(log_file_path: Path):
        with open(log_file_path) as log_file:
            log_content = log_file.read()
        for match in re.finditer(BenchmarkLatencyExtractor.LOG_REGEXP_PATTERN, log_content):
            cause = match.group(1)
            if (not LATENCY_FILTER_FULL or 'Pause Full' not in cause) and \
                (not LATENCY_FILTER_SYSTEM_GC or 'System.gc()' not in cause):
                yield GCLatency(log_file=log_file_path, gc_cause=match.group(1), latency=float(match.group(2)))

class BenchmarkSetLatencyExtractor:
    def __init__(self, benchmark_runs: BenchmarkRunLocator, name: str):
        self._benchmark_runs = benchmark_runs
        self._name = name

    def extract_latencies(self):
        for benchmark_run in self._benchmark_runs.locations:
            extractor = BenchmarkLatencyExtractor(benchmark_run.joinpath('benchmarks', self._name))
            yield from extractor.extract_latencies()

    def into_data_frame(self) -> pandas.DataFrame:
        def latency_gen():
            for gc_latency in self.extract_latencies():
                yield (gc_latency.gc_cause, gc_latency.latency)
        return pandas.DataFrame(latency_gen(), columns=['Cause', 'Latency'])

    def load(self) -> BenchmarkLatency:
        return BenchmarkLatency(benchmark_runs=self._benchmark_runs, name=self._name, data_frame=self.into_data_frame())

def aggregate_latency_for_runs(benchmark_runs: BenchmarkRunLocator) -> BenchmarkLatencyAggregation:
    benchmark_extractors = [
        BenchmarkSetLatencyExtractor(benchmark_runs, 'BigRamTesterS'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'CompilerSpeed'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'dacapo'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'dacapo_large'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'dacapo_huge'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'DelayInducer'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'jbb2005'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'optaplanner'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'pjbb2005'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'renaissance'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'rubykon'),
        BenchmarkSetLatencyExtractor(benchmark_runs, 'specjvm2008')
    ]
    benchmarks = [benchmark_extractor.load() for benchmark_extractor in benchmark_extractors]
    latency_aggregated = [benchmark.aggregate_latencies() for benchmark in benchmarks]
    cause_aggregated = [benchmark.aggregate_causes() for benchmark in benchmarks]
    return BenchmarkLatencyAggregation(latency=pandas.concat(latency_aggregated), causes=pandas.concat(cause_aggregated).fillna(0))

def plot_latencies(data_frame: pandas.DataFrame, benchmark_index: str, title: str, figsize=None):
    benchmark_names, _ = data_frame.columns.levels
    labels = list()
    bar_groups = dict()
    y_range = (math.inf, 0)
    row = data_frame.loc[[benchmark_index]]
    labels.append(benchmark_index)
    for benchmark_name in benchmark_names:
        bar_data = (benchmark_index, row.at[benchmark_index, (benchmark_name, 'mean')], row.at[benchmark_index, (benchmark_name, 'p05')], row.at[benchmark_index, (benchmark_name, 'p95')])
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
    y_range = expand_min_max(y_range[0], y_range[1], 1.1)
    
    ax.set_title(title)
    ax.set_ylabel('Mean latency, msec')
    ax.set_xticks(x, labels)
    ax.set_xlabel('Benchmark')
    ax.set_ylim(0, y_range[1])
    ax.legend(bbox_to_anchor = (0.5, -0.2), loc='upper center')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.grid(True, which='major', linestyle='solid')
    ax.yaxis.grid(True, which='minor', linestyle='dotted')

    content = BytesIO()
    fig.tight_layout()
    fig.savefig(content, bbox_inches='tight', dpi=300, format='png')
    plt.close()
    return content.getvalue()

def plot_counts(data_frame: pandas.DataFrame, benchmark_index: str, title: str, figsize=None):
    benchmark_names = data_frame.columns
    labels = list()
    bar_groups = dict()
    y_range = (math.inf, 0)
    row = data_frame.loc[[benchmark_index]]
    labels.append(benchmark_index)
    for benchmark_name in benchmark_names:
        bar_data = (benchmark_index, row.at[benchmark_index, benchmark_name])
        if benchmark_name not in bar_groups:
            bar_groups[benchmark_name] = list()
        bar_groups[benchmark_name].append(bar_data)
        y_range = (
            min(y_range[0], bar_data[1]),
            max(y_range[1], bar_data[1])
        )
    
    fig = plt.figure(figsize=figsize or (25, 10))
    ax = fig.add_subplot()
    x = np.arange(len(labels))
    group_width = 1.0 / len(labels)
    bar_width = 0.5 / len(bar_groups)
    bar_offset = -0.25
    for bar_label, bars in bar_groups.items():
        bar_values = [
            count
            for _, count in bars
        ]
        ax.bar(x + bar_offset, bar_values, bar_width, label=bar_label)
        bar_offset += bar_width
    y_range = expand_min_max(0, y_range[1], 1.1)
    
    ax.set_title(title)
    ax.set_ylabel('Number of GCs')
    ax.set_xticks(x, labels)
    ax.set_xlabel('Benchmark')
    ax.set_ylim(y_range[0], y_range[1])
    ax.legend(bbox_to_anchor = (0.5, -0.2), loc='upper center')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.grid(True, which='major', linestyle='solid')
    ax.yaxis.grid(True, which='minor', linestyle='dotted')

    content = BytesIO()
    fig.tight_layout()
    fig.savefig(content, bbox_inches='tight', dpi=300, format='png')
    plt.close()
    return content.getvalue()

def run(args: List[str]):
    archive_output = args[1]
    benchmark_run_sets = locate_benchmark_runs(args[2:])
    baseline_benchmark_runs = benchmark_run_sets[0]

    aggregation = [aggregate_latency_for_runs(benchmark_runs) for benchmark_runs in benchmark_run_sets]
    latencies = pandas.concat([aggregate.latency for aggregate in aggregation],
        keys=[benchmark_runs.name for benchmark_runs in benchmark_run_sets],
        axis=1)
    causes = pandas.concat([aggregate.causes for aggregate in aggregation],
        keys=[benchmark_runs.name for benchmark_runs in benchmark_run_sets],
        axis=1)

    gc_counts = latencies.loc[:, (latencies.columns.get_level_values(1) == 'count')]
    gc_counts = gc_counts.droplevel(1, axis=1)

    bigramtester_latency_plot = plot_latencies(latencies, 'BigRamTesterS', 'BigRamTesterS GC Latencies')
    compiler_speed_latency_plot = plot_latencies(latencies, 'CompilerSpeed', 'CompilerSpeed GC Latencies')
    dacapo_latency_plot = plot_latencies(latencies, 'dacapo', 'DaCapo GC Latencies')
    dacapo_large_latency_plot = plot_latencies(latencies, 'dacapo_large', 'DaCapo Large GC Latencies')
    dacapo_huge_latency_plot = plot_latencies(latencies, 'dacapo_huge', 'DaCapo Huge GC Latencies')
    delay_inducer_latency_plot = plot_latencies(latencies, 'DelayInducer', 'DelayInducer GC Latencies')
    jbb2005_latency_plot = plot_latencies(latencies, 'jbb2005', 'jbb2005 GC Latencies')
    optaplanner_latency_plot = plot_latencies(latencies, 'optaplanner', 'Optaplanner GC Latencies')
    pjbb2005_latency_plot = plot_latencies(latencies, 'pjbb2005', 'pjbb2005 GC Latencies')
    renaissance_latency_plot = plot_latencies(latencies, 'renaissance', 'Renaissance GC Latencies')
    rubykon_latency_plot = plot_latencies(latencies, 'rubykon', 'Rubykon GC Latencies')
    specjvm2008_latency_plot = plot_latencies(latencies, 'specjvm2008', 'specjvm2008 GC Latencies')

    bigramtester_count_plot = plot_counts(gc_counts, 'BigRamTesterS', 'BigRamTesterS: Number of GCs')
    compiler_speed_count_plot = plot_counts(gc_counts, 'CompilerSpeed', 'CompilerSpeed: Number of GCs')
    dacapo_count_plot = plot_counts(gc_counts, 'dacapo', 'DaCapo: Number of GCs')
    dacapo_large_count_plot = plot_counts(gc_counts, 'dacapo_large', 'DaCapo Large: Number of GCs')
    dacapo_huge_count_plot = plot_counts(gc_counts, 'dacapo_huge', 'DaCapo Huge: Number of GCs')
    delay_inducer_count_plot = plot_counts(gc_counts, 'DelayInducer', 'DelayInducer: Number of GCs')
    jbb2005_count_plot = plot_counts(gc_counts, 'jbb2005', 'jbb2005: Number of GCs')
    optaplanner_count_plot = plot_counts(gc_counts, 'optaplanner', 'Optaplanner: Number of GCs')
    pjbb2005_count_plot = plot_counts(gc_counts, 'pjbb2005', 'pjbb2005: Number of GCs')
    renaissance_count_plot = plot_counts(gc_counts, 'renaissance', 'Renaissance: Number of GCs')
    rubykon_count_plot = plot_counts(gc_counts, 'rubykon', 'Rubykon: Number of GCs')
    specjvm2008_count_plot = plot_counts(gc_counts, 'specjvm2008', 'specjvm2008: Number of GCs')

    with zipfile.ZipFile(archive_output, 'w') as archive:
        archive.writestr('latencies.csv', latencies.to_csv())
        archive.writestr('causes.csv', causes.to_csv())

        archive.writestr('plots/latency/BigRamTesterS.png', bigramtester_latency_plot)
        archive.writestr('plots/latency/CompilerSpeed.png', compiler_speed_latency_plot)
        archive.writestr('plots/latency/DaCapo.png', dacapo_latency_plot)
        archive.writestr('plots/latency/DaCapo_Large.png', dacapo_large_latency_plot)
        archive.writestr('plots/latency/DaCapo_Huge.png', dacapo_huge_latency_plot)
        archive.writestr('plots/latency/DelayInducer.png', delay_inducer_latency_plot)
        archive.writestr('plots/latency/jbb2005.png', jbb2005_latency_plot)
        archive.writestr('plots/latency/Optaplanner.png', optaplanner_latency_plot)
        archive.writestr('plots/latency/pjbb2005.png', pjbb2005_latency_plot)
        archive.writestr('plots/latency/Renaissance.png', renaissance_latency_plot)
        archive.writestr('plots/latency/Rubykon.png', rubykon_latency_plot)
        archive.writestr('plots/latency/specjvm2008.png', specjvm2008_latency_plot)

        archive.writestr('plots/gc_count/BigRamTesterS.png', bigramtester_count_plot)
        archive.writestr('plots/gc_count/CompilerSpeed.png', compiler_speed_count_plot)
        archive.writestr('plots/gc_count/DaCapo.png', dacapo_count_plot)
        archive.writestr('plots/gc_count/DaCapo_Large.png', dacapo_large_count_plot)
        archive.writestr('plots/gc_count/DaCapo_Huge.png', dacapo_huge_count_plot)
        archive.writestr('plots/gc_count/DelayInducer.png', delay_inducer_count_plot)
        archive.writestr('plots/gc_count/jbb2005.png', jbb2005_count_plot)
        archive.writestr('plots/gc_count/Optaplanner.png', optaplanner_count_plot)
        archive.writestr('plots/gc_count/pjbb2005.png', pjbb2005_count_plot)
        archive.writestr('plots/gc_count/Renaissance.png', renaissance_count_plot)
        archive.writestr('plots/gc_count/Rubykon.png', rubykon_count_plot)
        archive.writestr('plots/gc_count/specjvm2008.png', specjvm2008_count_plot)

if __name__ == '__main__':
    try:
        run(sys.argv)
    except:
        traceback.print_exc()
