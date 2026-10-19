#!/usr/bin/env python3
"""Export the matched full a0/a112 figure for the A report; only eligible cases are plotted."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, ScalarFormatter
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parents[1]
FULL = ROOT / 'results/cluster-full-20261019'
JOBS = [('Baseline a0', 'expt_a0', 977740), ('Colocated a112', 'expt_a112', 977773)]
OUT = ROOT / 'docs/figures'
STEM = 'workload-a-full-matched'


def rows(file):
    with file.open() as source:
        return list(csv.DictReader(source))


def folder(expt, job):
    return FULL / 'citus_project_team_14' / expt / 'slurm-results' / f'job-{job}' / 'benchmark-results'


def main():
    OUT.mkdir(exist_ok=True)
    review = rows(FULL / 'case-review.csv')
    for _, expt, job in JOBS:
        cases = [r for r in review if r['experiment'] == expt and int(r['job_id']) == job]
        assert [int(r['clients']) for r in cases] == [1, 4, 8, 16, 32, 64]
        assert all(r['eligible'] == 'True' for r in cases), expt
    summaries = {expt: rows(folder(expt, job) / 'summary.csv') for _, expt, job in JOBS}
    clients = [int(r['clients']) for r in summaries['expt_a0']]
    tps = {expt: [int(r['successful_transactions']) / 600 for r in s] for expt, s in summaries.items()}
    shares = []
    for name, expt, job in JOBS:
        selected = [r for r in rows(folder(expt, job) / 'transaction_metrics.csv') if r['clients'] == '1']
        times = {r['transaction']: int(r['successful_transactions']) * float(r['avg_latency_ms']) for r in selected}
        total = sum(times.values())
        share = {k: 100 * times[k] / total for k in ['T3', 'T4', 'T6']}
        share['Other'] = 100 - sum(share.values())
        shares.append(dict(design=name, denominator_ms=total, **share))
    contract = dict(
        question='Does join-key colocation (a112) improve Workload A over a matched original baseline?',
        takeaway='a112 completes 17-28x more scripts per second at every client count; T6 now dominates its recorded time.',
        surface='Static figure for the Google Docs / PDF course report',
        renderer='Matplotlib; PNG and SVG exports',
        matplotlib_version=matplotlib.__version__,
        families=['ordered numeric line (log y)', '100% stacked horizontal bar'],
        sufficiency='Six client counts per design, one 600 s observation each on the same xcnf0-4 nodes; no confidence intervals.',
        palette_policy='Blue/gold/teal plus neutrals; dashed/square versus solid/circle distinguishes designs without color.',
        footprint_inches=[6.5, 6.5],
        google_docs_width_pt=420,
        sources=[str(folder(e, j).relative_to(ROOT)) for _, e, j in JOBS],
    )
    (OUT / f'{STEM}.contract.json').write_text(json.dumps(contract, indent=2) + '\n')
    (OUT / f'{STEM}.data.json').write_text(json.dumps(dict(clients=clients, tps=tps, one_client_time_shares=shares), indent=2) + '\n')
    blue, gold, teal, ink, grey = '#2864B4', '#E3B34D', '#2A9D8F', '#252B33', '#66717F'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11.5,
                         'axes.labelcolor': ink, 'text.color': ink,
                         'xtick.color': ink, 'ytick.color': ink, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'cs5424-team14-a-full-matched'})
    fig = plt.figure(figsize=(6.5, 6.5), facecolor='white')
    fig.text(.08, .965, 'Workload A: matched baseline vs colocation', fontsize=15, weight='bold')
    fig.text(.08, .926, 'Scale 1 · 600 s measurements · same xcnf0–4 nodes', fontsize=11.5)
    ax = fig.add_axes([.12, .535, .82, .29])
    ax.plot(clients, tps['expt_a0'], '--s', color=grey, markerfacecolor='white', markersize=5, linewidth=1.5, label='a0 baseline')
    ax.plot(clients, tps['expt_a112'], '-o', color=blue, markersize=5, linewidth=1.5, label='a112 colocated')
    for x, y0, y1 in zip(clients, tps['expt_a0'], tps['expt_a112']):
        ax.annotate(f'{y1 / y0:.0f}×', (x, y1), textcoords='offset points', xytext=(0, 7), ha='center', fontsize=11.5, color=blue)
    ax.set_xscale('log', base=2)
    ax.set_xticks(clients)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_yscale('log')
    ax.set_ylim(1, 300)
    ax.yaxis.set_major_locator(FixedLocator([1, 3, 10, 30, 100]))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_locator(FixedLocator([]))
    ax.set_xlabel('Clients', labelpad=3)
    ax.set_ylabel('Scripts / second (log)')
    ax.set_title('Completed-script throughput', loc='left', fontsize=12, pad=8)
    ax.grid(axis='y', color='#DDE1E7', linewidth=.6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(loc='center right', ncol=1, fontsize=11.5, frameon=False)
    bar = fig.add_axes([.27, .23, .67, .15])
    left = [0., 0.]
    for key, color, text_color in [('T3', blue, 'white'), ('T4', gold, ink), ('T6', teal, 'white'), ('Other', '#D9DEE5', ink)]:
        values = [r[key] for r in shares]
        bar.barh([0, 1], values, left=left, height=.55, color=color, edgecolor='white', linewidth=.7, label=key)
        for y, value, start in zip([0, 1], values, left):
            if value >= 8:
                bar.text(start + value / 2, y, f'{value:.0f}%', ha='center', va='center', color=text_color, fontsize=11.5)
        left = [start + value for start, value in zip(left, values)]
    bar.set_xlim(0, 100)
    bar.set_yticks([0, 1], [r['design'] for r in shares])
    bar.invert_yaxis()
    bar.set_xticks([])
    bar.tick_params(axis='y', length=0, pad=8)
    bar.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    bar.set_title('Recorded transaction time at one client', loc='left', fontsize=12, pad=9)
    bar.legend(loc='upper center', bbox_to_anchor=(.45, -.03), ncol=4, frameon=False, fontsize=11.5)
    fig.text(.08, .14, 'Time share = completed count × mean latency; shares rounded.', fontsize=11.5)
    fig.text(.08, .095, 'a0: 2/20/64/59 serialization failures at 8/16/32/64 clients.', fontsize=11.5)
    fig.text(.08, .055, 'a112: 0 failures (≤16 retried); validation passed at every count.', fontsize=11.5)
    fig.text(.08, .015, 'TPS = count / 600 s. Jobs 977740 (a0), 977773 (a112), seed 42.', fontsize=11.5)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in fig.findobj(match=Text):
        if not text.get_visible() or not text.get_text():
            continue
        box = text.get_window_extent(renderer)
        assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= fig.bbox.x1 and box.y1 <= fig.bbox.y1, text.get_text()
    fig.savefig(OUT / f'{STEM}.png', dpi=200)
    vector = OUT / f'{STEM}.svg'
    fig.savefig(vector, metadata={'Date': None})
    vector.write_text('\n'.join(line.rstrip() for line in vector.read_text().splitlines()) + '\n')
    plt.close(fig)
    print(OUT / f'{STEM}.png')


if __name__ == '__main__':
    main()
