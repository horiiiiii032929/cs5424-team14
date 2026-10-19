#!/usr/bin/env python3
"""Export a source-backed figure for the A report; no aborted TPS is ranked."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'citus_project_team_14/expt_a0/slurm-results/job-918524/benchmark-results'
INDEX = ROOT / 'results/cluster-import-20261019/expt_a102/slurm-results/job-965657/benchmark-results'
OUT = ROOT / 'docs/figures'


def rows(file):
    with file.open() as source:
        return list(csv.DictReader(source))


def main():
    OUT.mkdir(exist_ok=True)
    a0, a102 = rows(BASE / 'summary.csv'), rows(INDEX / 'summary.csv')
    clients = [int(r['clients']) for r in a0]
    assert clients == [1, 4, 8, 16, 32, 64]
    assert clients == [int(r['clients']) for r in a102]
    assert all(int(r['pgbench_exit_code']) == 0 for r in a0 + a102)
    contract = dict(
        question='How do lookup indexes affect throughput and the dominant read costs?',
        takeaway='Concurrent throughput improves in the observed runs, while T3/T4 still dominate recorded time.',
        surface='Static figure for the Google Docs / PDF course report',
        renderer='Matplotlib; PNG and SVG exports',
        matplotlib_version=matplotlib.__version__,
        families=['ordered numeric line', '100% stacked horizontal bar'],
        sufficiency='Six configured non-temporal client counts per design; one observation each, no confidence intervals.',
        palette_policy='Blue and gold plus neutrals; dashed/square versus solid/circle distinguishes designs without color.',
        footprint_inches=[6.5, 6.5],
        caveat='a102/c16 warmup exited 2; its completed measurement is shown with a hollow diamond and excluded from clean-run comparisons.',
        sources=[str(p.relative_to(ROOT)) for p in [BASE / 'summary.csv', INDEX / 'summary.csv', BASE / 'transaction_metrics.csv', INDEX / 'transaction_metrics.csv']],
    )
    shares = []
    for name, folder in [('Baseline a0', BASE), ('Indexes a102', INDEX)]:
        selected = [r for r in rows(folder / 'transaction_metrics.csv') if r['clients'] == '1']
        times = {r['transaction']: int(r['successful_transactions']) * float(r['avg_latency_ms']) for r in selected}
        total = sum(times.values())
        shares.append(dict(design=name, denominator_ms=total, T3=100 * times['T3'] / total,
                           T4=100 * times['T4'] / total,
                           Other=100 * (total - times['T3'] - times['T4']) / total))
    (OUT / 'workload-a-baseline-indexes.contract.json').write_text(json.dumps(contract, indent=2) + '\n')
    (OUT / 'workload-a-baseline-indexes.data.json').write_text(json.dumps(dict(a0=a0, a102=a102, one_client_time_shares=shares), indent=2) + '\n')
    blue, gold, ink, grey = '#2864B4', '#E3B34D', '#252B33', '#66717F'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11.5,
                         'axes.labelcolor': ink, 'text.color': ink,
                         'xtick.color': ink, 'ytick.color': ink, 'svg.fonttype': 'none'})
    fig = plt.figure(figsize=(6.5, 6.5), facecolor='white')
    fig.text(.08, .965, 'Workload A: baseline and lookup indexes', fontsize=15, weight='bold')
    fig.text(.08, .926, 'Scale 1 · 600 s measurements · one run per client count', fontsize=11.5)
    ax = fig.add_axes([.12, .535, .82, .29])
    tps0 = [float(r['overall_tps']) for r in a0]
    tps102 = [float(r['overall_tps']) for r in a102]
    ax.plot(clients, tps0, '--s', color=grey, markerfacecolor='white', markersize=5, linewidth=1.5, label='a0 baseline')
    ax.plot(clients, tps102, '-', color=blue, linewidth=1.5, label='a102 indexes')
    clean = [i for i, client in enumerate(clients) if client != 16]
    ax.scatter([clients[i] for i in clean], [tps102[i] for i in clean], color=blue, s=28, zorder=3)
    ax.scatter([16], [tps102[3]], marker='D', facecolor='white', edgecolor=blue,
               linewidth=1.5, s=45, zorder=4, label='Warmup aborted')
    ax.set_xscale('log', base=2)
    ax.set_xticks(clients)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_ylim(0, 4.5)
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_xlabel('Clients', labelpad=3)
    ax.set_ylabel('Scripts / second')
    ax.set_title('Completed-script throughput', loc='left', fontsize=12, pad=8)
    ax.grid(axis='y', color='#DDE1E7', linewidth=.6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(loc='lower left', ncol=2, fontsize=11, frameon=False, columnspacing=1)
    bar = fig.add_axes([.25, .23, .69, .15])
    left = [0., 0.]
    for key, color, text_color in [('T3', blue, 'white'), ('T4', gold, ink), ('Other', '#D9DEE5', ink)]:
        values = [r[key] for r in shares]
        bar.barh([0, 1], values, left=left, height=.55, color=color,
                 edgecolor='white', linewidth=.7, label=key)
        for y, value, start in zip([0, 1], values, left):
            bar.text(start + value / 2, y, f'{value:.0f}%', ha='center', va='center', color=text_color, fontsize=11)
        left = [start + value for start, value in zip(left, values)]
    bar.set_xlim(0, 100)
    bar.set_yticks([0, 1], [r['design'] for r in shares])
    bar.invert_yaxis()
    bar.set_xticks([])
    bar.tick_params(axis='y', length=0, pad=8)
    bar.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    bar.set_title('Recorded transaction time at one client', loc='left', fontsize=12, pad=9)
    bar.legend(loc='upper center', bbox_to_anchor=(.5, -.03), ncol=3, frameon=False, fontsize=11)
    fig.text(.08, .14, 'Time share = completed count × mean latency; shares rounded.', fontsize=11)
    fig.text(.08, .095, 'Hollow point: a102/16-client warmup aborted; measurement completed.', fontsize=11)
    fig.text(.08, .055, 'a0: 25/51/50 serialization failures at 16/32/64 clients.', fontsize=11)
    fig.text(.08, .015, 'TPS = count / 600 s. Jobs: 918524 (a0), 965657 (a102; Kelvin).', fontsize=11)
    fig.savefig(OUT / 'workload-a-baseline-indexes.png', dpi=200)
    fig.savefig(OUT / 'workload-a-baseline-indexes.svg')
    plt.close(fig)
    print(OUT / 'workload-a-baseline-indexes.png')


if __name__ == '__main__':
    main()
