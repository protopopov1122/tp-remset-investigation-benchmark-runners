#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path
from typing import List
import zipfile
from loaders import *

def run(args: List[str]):
    archive_output = args[1]
    benchmark_runs = [Path(arg) for arg in args[2:]]
    compiler_speed = load_compiler_speed(benchmark_runs)
    dacapo = load_dacapo(benchmark_runs, 'dacapo')
    dacapo_large = load_dacapo(benchmark_runs, 'dacapo_large')
    dacapo_huge = load_dacapo(benchmark_runs, 'dacapo_huge')
    delay_inducer = load_delay_inducer(benchmark_runs)
    jbb2005 = load_jbb2005(benchmark_runs)
    optaplanner = load_optaplanner(benchmark_runs)
    pjbb2005_msec, pjbb2005_throughput = load_pjbb2005(benchmark_runs)
    renaissance = load_renaissance(benchmark_runs)
    rubykon = load_rubykon(benchmark_runs)
    specjvm2008 = load_specjvm2008(benchmark_runs)

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
