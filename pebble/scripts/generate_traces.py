#!/usr/bin/env python3
"""Capture schedules from the checked-out manuscript C++ implementation."""
import json
import hashlib
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
repo_path = os.environ.get('PEBBLE_REPO')
if not repo_path:
    raise SystemExit('Set PEBBLE_REPO to a checkout of https://github.com/red1108/pebble before regenerating traces.')
REPO = Path(repo_path).expanduser().resolve()
if not (REPO / 'applications/complete_trees/measure.cpp').is_file():
    raise SystemExit(f'PEBBLE_REPO does not contain the expected pebble sources: {REPO}')
BUILD = ROOT / '.generated'
OUT = ROOT / 'traces'


def compile_one(source, out, includes):
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    cmd = compiler + ['-std=c++17', '-O2', '-UNDEBUG']
    for path in includes:
        cmd += ['-I', str(path)]
    subprocess.run(cmd + [str(source), '-o', str(out)], check=True)


def tree_run(kind, height, budget):
    text = subprocess.check_output([str(BUILD / 'measure'), kind, str(height),
                                    str(budget), 'trace'], text=True).splitlines()
    metrics = json.loads(text[0])
    rounds = []
    for line in text[1:]:
        row = {'p': [], 'u': [], 'g': []}
        for op in line.split():
            row[{'P': 'p', 'U': 'u', 'G': 'g'}[op[0]]].append(int(op[1:]))
        rounds.append(row)
    assert len(rounds) == metrics['depth']
    return {'kind': kind, 'graph': 'tree', 'height': height, 'budget': budget,
            'initial': [], 'rounds': rounds, 'metrics': metrics,
            'source': f'{kind} native scheduler, H={height}, s={budget}'}


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    compile_one(REPO / 'applications/complete_trees/measure.cpp', BUILD / 'measure', [REPO / 'core'])
    compile_one(ROOT / 'scripts/kmrv_trace.cpp', BUILD / 'kmrv_trace', [REPO / 'cli', REPO / 'core'])
    traces = {kind: tree_run(kind, 3, 4) for kind in ('kss', 'sequential', 'parallel')}
    traces['kss4'] = tree_run('kss', 4, 5)
    traces['sequential4'] = tree_run('sequential', 4, 5)
    # KMRV is the paper's retained-endpoint prefix-path schedule. The anchor
    # is a permanent pebble; preparation of actual input values is not shown.
    length = 7
    kmrv = json.loads(subprocess.check_output([str(BUILD / 'kmrv_trace'), str(length)], text=True))
    traces['kmrv'] = {'kind': 'kmrv', 'graph': 'path', 'length': length,
                      'initial': [0], 'rounds': kmrv,
                      'source': 'KMRV retained-endpoint path; anchor fixed; inputs excluded'}
    traces['revision'] = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
    tracked = ['core/quantum_computer.hpp', 'core/pebbling_common.hpp',
               'core/sequential_schedule.hpp', 'core/complete_tree_schedule.hpp',
               'core/kss_schedule.hpp', 'core/parallel_schedule.hpp',
               'applications/complete_trees/measure.cpp', 'cli/kmrv.cpp']
    traces['source_sha256'] = {name: hashlib.sha256((REPO / name).read_bytes()).hexdigest()
                               for name in tracked}
    traces['source_changes'] = subprocess.check_output(
        ['git', '-C', str(REPO), 'status', '--porcelain', '--', *tracked], text=True).splitlines()
    (OUT / 'native.json').write_text(json.dumps(traces, indent=2) + '\n')
    source = (REPO / 'core/sequential_schedule.hpp').read_text()
    start = source.index('template<class Computer>\nvoid sequential_pebble(')
    end = source.index('\ntemplate<class Computer>\nvoid contract(', start)
    (ROOT / 'snippets').mkdir(exist_ok=True)
    (ROOT / 'snippets/sequential_pebble.cpp').write_text(source[start:end].rstrip() + '\n')
    for key in ('kss', 'sequential', 'parallel', 'kss4', 'sequential4', 'kmrv'):
        print(f'{key}: {len(traces[key]["rounds"])} steps')


if __name__ == '__main__':
    main()
