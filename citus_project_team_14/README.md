# Team 14 experiments

`expt_a0` and `expt_b0` are Dessi's preserved baseline snapshots (jobs 918524 and
918781). `expt_a101`–`expt_a115` are Hikaru's proposed Task 2 experiments. Each
folder contains a complete run.sh, transactions and any supporting SQL.
New IDs must be checked against current team work. a109/a110 isolate the
read-only access declaration relative to a101/a108. a111 adapts Dessi's B b1/b2
placement on a102; a112 adds read-only access declarations to a111. All new
variants require xcnf nodes. a113 adds DEFERRABLE to a112's read-only transactions
to test safe-snapshot waits without lowering isolation. a114 adds a104's exact
daily sales summaries to a112, striped eight ways per merchant/day to limit
hot-row upsert conflicts; T6 reads the summary plus only the two partial-day
order ranges under READ ONLY. a115 is its control: a112 plus only the
`orders(created_at)` index, with a112's original T6 query.

| Experiment | Change from baseline |
|---|---|
| expt_a101 | Merchant colocation |
| expt_a102 | Lookup indexes |
| expt_a103 | One-call place order |
| expt_a104 | Exact sales summaries |
| expt_a105 | work_mem 64MB |
| expt_a106 | Executor pool 2 |
| expt_a107 | Executor pool 8 |
| expt_a108 | Colocation + indexes + one-call order + summary |
| expt_a109 | Merchant colocation + declared read-only queries |
| expt_a110 | Combined design + declared read-only queries |
| expt_a111 | Lookup indexes + product/order join colocation |
| expt_a112 | Product/order join colocation + read-only queries |
| expt_a113 | Product/order join colocation + READ ONLY DEFERRABLE |
| expt_a114 | a112 + exact daily sales summaries (8 stripes) |
| expt_a115 | a112 + orders(created_at) index only (a114 control) |

`expt_b1`–`expt_b6` are Desmond's Workload B optimization experiments. Each
folder contains a complete run.sh, transactions, Slurm output and benchmark
results. `expt_b201` is the submission alias for the supplementary T7-only
experiment; its original server name is retained below for reference.

| Experiment | Change from baseline |
|---|---|
| expt_b0 | Baseline Workload B |
| expt_b1 | Inventory/product colocation and routed T7 updates |
| expt_b2 | Order-items/orders colocation |
| expt_b3 | Covering T6 index and VACUUM |
| expt_b4 | READ ONLY queries, coordinator T6 timestamps and plan capture |
| expt_b5 | Merchant/customer order index |
| expt_b6 | Daily-sales rollup for T6 |
| expt_b201 | T7-only placement experiment (`expt_xc_b1`) |

The matched b0/b6 jobs are stored under `expt_b0` and `expt_b6`; b6 also
contains the separate correctness jobs and their supporting scripts.
