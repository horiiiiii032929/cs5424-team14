#!/usr/bin/env python3
"""One-time report reconciliation against the user-supplied assignment overview."""
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'submission/report/report.md'
s=path.read_text()
if '## `expt_a0`: baseline protocol and results' in s:
    raise SystemExit('Assignment reconciliation is already present; edit the report directly.')

def paragraph(prefix):
    return next(p for p in s.split('\n\n') if p.startswith(prefix))

def table(file,columns):
    rows=list(csv.DictReader(file.open()))
    out='| '+' | '.join(label for _,label in columns)+' |\n'
    out+='| '+' | '.join('---' for _ in columns)+' |\n'
    for r in rows:
        out+='| '+' | '.join(r[key] for key,_ in columns)+' |\n'
    return out

baseline=ROOT/'citus_project_team_14/expt_a0/slurm-results/job-918524/benchmark-results/summary.csv'
base_table=table(baseline,[('clients','Clients'),('overall_tps','TPS'),('overall_median_latency_ms','p50 ms'),('overall_p95_latency_ms','p95 ms'),('overall_p99_latency_ms','p99 ms'),('serialization_failures','Serial. failures')])
s=s.replace('# 2. Task 1: Baseline design for workload A\n', '# 2. Task 1: Baseline design for workload A\n\n## `expt_a0`: baseline protocol and results\n')
old=paragraph('Source: preserved expt_a0/')
s=s.replace(old,base_table+'\nTable 2.1. Baseline A (job 918524), with latency percentiles in milliseconds. All measured exits are zero; the final three client counts retain serialization failures.\n\nSource: `expt_a0/slurm-results/job-918524/benchmark-results/summary.csv`, `transaction_metrics.csv` and `config.txt` in the submitted result archive.')

old_a=s[s.index('# 3. Task 2:'):s.index('## Write-path experiments')]
parts=['# 3. Task 2: Optimized design for workload A',
    'The objective is average transaction throughput, with latency percentiles, retries and failures retained to assess the trade-offs. The main progression is a0 to a102 (lookup indexes), a111 (join-key colocation), and a112 (read-only declarations). a113, a114 and a115 test alternative follow-ups. Short diagnostics and cross-allocation comparisons are distinguished from the matched full a0/a112 matrix; the final combined improvement does not isolate each component\'s effect.',
    '## `expt_a102`: lookup indexes',
    paragraph("Kelvin's a102 job"),
    paragraph('All six measured a102 exits'),
    '![A figure](images/workload-a-baseline-indexes.pdf)',
    paragraph('Figure 3.1.'),
    'At one client, T7 mean latency falls from 51.114 to 13.709 ms, while T3/T4 remain 2668.472/454.362 ms. The indexes help individual operations but do not remove the dominant distributed-read cost.',
    '## `expt_a101`: merchant colocation and failed diagnostics',
    'a101 distributes merchant-owned data by merchant_id to make merchant-scoped operations local. Its small-fixture four-client cases aborted. In the cluster smoke suite, a101/job 977433 also aborted at four clients. The scale-1 diagnostic (job 977468) aborted in warmup and measurement, so its partial throughput is not ranked. These negative results motivated join-key rather than wholesale merchant colocation. The original slow post-run global-ID validator was replaced by equivalent exact checks; seven deliberate-corruption tests verified the replacement. Validation runs outside the timed interval.',
    '## `expt_a111`: join-key colocation',
    'a111 adapts the B team\'s placement ideas on top of a102: inventory is colocated with products by product_id, and order_items with orders by order_id; T7 uses the corresponding routing predicates. This targets the joins used by T3/T4 while retaining query semantics, SERIALIZABLE isolation, workload weights, durability and retry limits. a112 adds READ ONLY declarations to T3/T4/T6 relative to a111.',
    '## `expt_a113`: safe-snapshot control against a111 and a112',
    'a113 adds READ ONLY DEFERRABLE to a112\'s read transactions. The scale-1/four-client diagnostics used the original workload mix, 60-second warmups and 60-second measurements. All three completed both phases without measured failures or retries and passed exact validation.',
    '| Experiment | Job | Change | TPS |\n| --- | --- | --- | --- |\n| `expt_a111` | 977617 | Join-key colocation on a102 | 89.917 |\n| `expt_a112` | 977618 | a111 plus READ ONLY | 92.383 |\n| `expt_a113` | 977619 | a112 plus DEFERRABLE | 90.550 |',
    'Table 3.1. Diagnostic progression and safe-snapshot control. These single 60-second observations do not establish a reliable ranking or a general concurrency fix.',
    '## `expt_a112`: matched full comparison and repeat',
    paragraph('Full matched a0/a112 jobs'),
    paragraph('At 1/4/8/16/32/64 clients, fresh a0 TPS'),
    paragraph('At one client, T3 fell'),
    paragraph('Repeat a112 job'),
    '![A figure](images/workload-a-full-matched.pdf)',
    paragraph('Figure 3.2.')]
full=ROOT/'results/cluster-full-20261019/citus_project_team_14/expt_a112/slurm-results/job-977773/benchmark-results/summary.csv'
parts += [table(full,[('clients','Clients'),('overall_tps','TPS'),('overall_median_latency_ms','p50 ms'),('overall_p95_latency_ms','p95 ms'),('overall_p99_latency_ms','p99 ms'),('retried_transactions','Retried txns')]),
    'Table 3.2. Full a112 job 977773. All six warmup/measurement exits are zero and all measured failed-record counts are zero. A retry count is the number of retried transactions, not the number of final failures.',
    '## `expt_a114`: maintained summaries as a negative result',
    'a114 adds exact daily sales summaries to a112, with eight stripes per merchant/day to reduce write contention. At scale 1/four clients, job 979865 achieved 85.333 TPS and T6 mean latency 764.5 ms, compared with a112 diagnostic 92.383 TPS and T6 650.6 ms. Core and exact-summary checks passed, but this single observation provides no performance benefit and a114 is not recommended.',
    '## `expt_a115`: timestamp-index control and reliability trade-off',
    'a115 adds only orders(created_at) to a112 and retains its original T6 query. Diagnostic job 979866 achieved 288.633 TPS, T6 mean latency 115.9 ms, zero failed transactions and two retried transactions/two retry attempts, with passing validation. This isolates a useful timestamp-index hypothesis relative to a114\'s more complex summary design; a short diagnostic does not establish full-matrix reliability.',
    'Full seed-42/seed-7 jobs 979909/979910 provide 12 client-count cases on xcnf0-4. Seven cases complete both phases: seed 42 at 1/4/8/16 clients (c4 has one final serialization failure) and seed 7 at 1/4/32. Six cases have zero failed records. Seed-42 c32/c64 and seed-7 c8/c16/c64 measurements exit 2; both c64 warmups exit 2. All 12 core validations pass and 26 runtime source-hash comparisons match. Passing integrity checks do not turn an aborted performance run into a clean comparison.',
    paragraph('At one client both a115 seeds pass'),
    '## Supporting implementations and validation scope',
    'Local-only variants a103-a108 and a109/a110 explore one-call T1, maintained summaries, memory/executor settings and read-only declarations. Their source is retained under `supporting_implementations/local_only/` and their small-scale outputs under `evidence/local-only/`; they are not course-cluster benchmark experiments. The original distributed correctness suite passed 138 checks. Follow-up a109/a110 passed 26/38 checks and a111/a112/a113 passed 29 each (151 in total). Tests exercised actual read scripts, placement metadata and transfers with inventory IDs different from product IDs. Seven local four-client follow-up stress cases aborted; all 45 post-failure integrity checks passed. The local hot-merchant fixture differs from the full cluster dataset, so its timings are not ranked as cluster evidence.',
    '## Write-path experimental method']
s=s.replace(old_a,'\n\n'.join(parts)+'\n\n')
s=s.replace('## Write-path experiments\n','')
s=s.replace('## `expt_a13` (not run)','## Unrun T7 rewrite proposal (a13)')
s=s.replace('In addition, we also ran a T7-only supplementary validation to isolate expt_b1‘s direct effect.',
    'The T7-only supplementary experiment `expt_b201` (originally expt_xc_b1, job 989344) and baseline expt_b0/job 988876 examine the intended routing effect. The baseline uses xcnc34-38 while the optimized run uses xcnf10-14, so this is not a hardware-matched isolated causal comparison.')
s=s.replace('This supports the intended routing benefit by eliminating the baseline\'s preliminary inventory_id lookups.',
    'The observation is consistent with the intended routing benefit, but different hardware prevents attributing the full change to the code alone.')
s=s.replace('To compare the final design with the baseline under the same conditions,',
    '### Matched baseline comparison and separate correctness run\n\nTo compare the final design with the baseline under the same conditions,')
path.write_text(s)
print('Reconciled report with experiment subsections, baseline/optimized percentile tables, and explicit local-only scope.')
