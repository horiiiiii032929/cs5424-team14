# Team 14 experiments

`expt_a0` and `expt_b0` are Dessi's preserved baseline snapshots (jobs 918524 and
918781). `expt_a101`–`expt_a113` are Hikaru's proposed Task 2 experiments. Each
folder contains a complete run.sh, transactions and any supporting SQL.
New IDs must be checked against current team work. a109/a110 isolate the
read-only access declaration relative to a101/a108. a111 adapts Dessi's B b1/b2
placement on a102; a112 adds read-only access declarations to a111. All new
variants require xcnf nodes. a113 adds DEFERRABLE to a112's read-only transactions
to test safe-snapshot waits without lowering isolation.

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
