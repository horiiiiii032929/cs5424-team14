# CS5424 Citus Project Notes

The project is worth **25 marks**. You will optimize a multi-tenant order-processing application on a distributed database, then use benchmarks to explain which changes improve performance and why.

**Deadline: Friday, 30 October 2026, 23:59.** The project brief specifies **Citus 14.1.0 with PostgreSQL 18.6**, running on the SoC compute cluster through Slurm. Use `psql` to interact with the database and `pgbench` to benchmark transactions.

## Deadline and proposed team split

**Submission deadline: 30 October 2026 at 23:59 Singapore time.**

- **Task 2, workload A:** two teammates optimize and benchmark workload A.
- **Task 4, workload B:** the other two teammates optimize and benchmark workload B.
- **Individual work proposed by Dessi:** each person comes up with 3–5 optimization ideas within their assigned workload, then coordinates experiments with their partner. This is a team suggestion, not a course requirement.
- **Shared team work:** assign owners for the Task 1 and Task 3 baseline runs, combine findings into one report, package submissions, and prepare for the week 13 Q&A. Each member's contributions must be listed in the report, and all members are expected at the Q&A.
- **Coordination proposed by Kelvin:** share a remote Git repository and use a Google Sheet to record who handles A or B. His supplied final message is incomplete.

Hori and Kelvin agreed to the general split; individual assignments and coordinator roles remain subject to team confirmation. Dessi's installation and baseline A/B snapshots are verified and preserved. For the 22 October implementation/results status, provisional A selection, imported B evidence and remaining a115 archive gap, see [current status](docs/project-status.md). The requirements below summarize the supplied assignment; dated progress belongs in that status page.

## What you need to do

| Task | Required work | Experiment naming |
| --- | --- | --- |
| 1 | Benchmark the baseline for workload A while varying concurrent clients. | `expt_a0` |
| 2 | Optimize workload A and measure the effect of your changes. | `expt_a1`, `expt_a2`, … |
| 3 | Benchmark the baseline for workload B while varying concurrent clients. | `expt_b0` |
| 4 | Optimize workload B and measure the effect of your changes. | `expt_b1`, `expt_b2`, … |
| 5 | Submit experiment files, the report, and AI usage documentation where applicable. | Team submission files |

The main optimization target is **average transaction throughput**. Additional baseline experiments may vary worker count, data skew, or dataset scale.

## Database schema and baseline distribution

Each merchant owns products, inventory, customers, orders, and order items.

| Table | Primary key | Main information and relationships |
| --- | --- | --- |
| `merchants` | `merchant_id` | Merchant name and region |
| `customers` | `customer_id` | Merchant, customer name, email, creation time |
| `products` | `product_id` | Merchant, product name, category, price |
| `inventory` | `inventory_id` | Merchant, product, stock quantity, update time |
| `orders` | `order_id` | Merchant, customer, status, total amount, creation time |
| `order_items` | `order_item_id` | Merchant, order, product, quantity, unit price |

The baseline distributes the five tables other than `merchants` by their individual primary keys: `customer_id`, `product_id`, `inventory_id`, `order_id`, and `order_item_id`. The listed distribution commands do not distribute `merchants`.

There are five explicit indexes, one on `merchant_id` in each distributed table. The usual foreign-key relationships are described in the brief but their constraints are omitted from the baseline schema.

**Explicit check constraints:**

- Inventory quantity must be at least zero.
- Order total amount must be at least zero.
- Order item quantity must be greater than zero.
- Order item unit price must be at least zero.

## Transactions and workload weights

Weights are the configured percentage for each transaction in the workload.

| Transaction | Operation | A | B |
| --- | --- | --- | --- |
| T1 | Place Order | 36% | 10% |
| T2 | Update Inventory | 20% | 10% |
| T3 | Customer Order History | 10% | 5% |
| T4 | Product Lookup | 10% | 5% |
| T5 | Update Order Status | 10% | 10% |
| T6 | Global Sales | 5% | 10% |
| T7 | Inventory Transfer | 5% | 30% |
| T8 | Update Customer | 2% | 10% |
| T9 | Update Product | 2% | 10% |

- **T1:** For a merchant and customer pair, retrieve the customer name and email, then create a pending order containing one to five order items.
- **T2:** Adjust a specified inventory record using merchant, inventory, and product identifiers. Preserve non-negative stock.
- **T3:** Retrieve information from orders and order items for the latest 20 orders of a merchant and customer pair, ordered by creation time descending.
- **T4:** Retrieve product and inventory information for a merchant and product pair.
- **T5:** Update the status of a specified order.
- **T6:** For a given time period, return the top 20 merchants by total order revenue, with merchant ID, order count, and revenue, sorted by revenue descending.
- **T7:** Transfer quantity T from a source product to a destination product. Preserve non-negative stock.
- **T8:** Update a customer's email for a merchant and customer pair.
- **T9:** Increase a specified product's price.

**Workload interpretation:** T1 and T2 account for 56% of A, while T7 alone accounts for 30% of B. Most transactions concern one merchant; some span merchants or the full database. These differences motivate separate optimization experiments for A and B.

## Dataset size and skew

At the default `SCALE=1`:

| Table | Rows |
| --- | ---: |
| merchants | 1,000 |
| customers | 1,000,000 |
| products | 500,000 |
| inventory | 500,000 |
| orders | 5,000,000 |
| order_items | 15,000,000 |

The default workload is skewed: **10% of merchants receive approximately 50% of order activity**.

## Cluster setup and experiment workflow

Enable SoC Compute Cluster access in MySoC. Use login nodes for access, job submission, and monitoring; run heavy computation on Slurm compute nodes.

For remote access, the brief gives this command, replacing `alice` with your account:

```bash
ssh -J alice@stujump.comp.nus.edu.sg alice@xlogin.comp.nus.edu.sg
```

Outside the NUS network, connect to NUS VPN first. The brief requires SSH public keys when connecting from within NUS, including SoC, without VPN.

Download the provided files on a login node:

```bash
cd "$HOME"
wget https://www.comp.nus.edu.sg/~cs4224/citus_project.zip
unzip citus_project.zip
cd citus_project
```

The download contains `expt_a0/`, `expt_b0/`, `install_citus_slurm.sh`, and `README.md`.

**Before submitting jobs:**

1. Set your notification email in the `#SBATCH --mail-user` directive in the installer and experiment scripts.
2. Replace the default team number 99 in `run.sh` with your actual `TEAM_ID` so teams use different PostgreSQL ports.
3. Install Citus once with `sbatch install_citus_slurm.sh`. The installation goes under `$HOME/pgsql`.
4. Submit each experiment's `run.sh` through Slurm.

```bash
chmod u+x *.sh
sbatch install_citus_slurm.sh

# After installation completes, run the workload A baseline.
cd expt_a0
chmod u+x *.sh
sbatch run.sh
squeue -u "$USER"
```

Each experiment contains `run.sh` and a `transactions/` directory with nine transaction SQL files. The two baseline directories differ only in the workload setting in `run.sh`.

The first allocated node acts as coordinator; the remaining nodes act as workers. The script initializes and starts the database servers, creates the schema, generates data, and runs pgbench.

The cluster home directory is shared across nodes through NFS and is **not backed up**. Node-local `/tmp` can be useful for heavy I/O. The brief suggests `umask u=rwx,g=,o=` in `~/.bash_profile` to restrict newly created files to your account.

## Benchmark metrics

**Throughput** measures completed transactions per second. **Latency** measures how long a transaction takes. Compare both as concurrent client count increases.

| Metric | How to interpret it |
| --- | --- |
| Overall TPS | Successfully logged transactions divided by the configured measured duration |
| Average latency | Arithmetic mean across successfully logged transactions |
| p50 or median | Approximately half of successful transactions finish at or below this latency |
| p95 | Approximately 95% finish at or below this latency |
| p99 | Approximately 99% finish at or below this latency; useful for identifying very slow transactions |
| Retried transactions | Transactions retried at least once |
| Total retries | All retry attempts; a transaction can contribute several |
| Serialization and deadlock failures | Failure counts reported by pgbench |
| Failed log records | Records without a numeric latency; investigate these |
| pgbench exit code | Zero means normal completion; non-zero indicates a run-level failure |

`summary.csv` contains workload-level results for each client count. `transaction_metrics.csv` contains per-transaction counts, TPS, and average/p50/p95/p99 latency for each client count.

The benchmark uses pgbench transaction logging with `-l`. The default `LOG_SAMPLE_RATE=1.0` includes every successfully logged transaction in latency calculations. Raw latency is in **microseconds**; the summary CSV files convert it to **milliseconds**.

Do not judge a design only by average latency. Check throughput, tail latency, retries, and failures together.

## Where to find results and diagnose failures

Each run creates `slurm-results/job-<slurm-job-id>/` within its experiment directory.

| File or directory | Purpose |
| --- | --- |
| `benchmark.log` | First log to inspect when pgbench fails |
| `schema-create.log` | Schema creation log |
| `data-generation.log` | Synthetic data generation log |
| `server_versions.log` | PostgreSQL and Citus versions |
| `topology.txt` | Coordinator and worker node allocation |
| `<hostname>-postgresql.log` | Database server log for each node |
| `benchmark-results/config.txt` | Benchmark configuration |
| `benchmark-results/summary.csv` | Main workload results |
| `benchmark-results/transaction_metrics.csv` | Main per-transaction results |
| `result-cN.txt` and `warmup-cN.txt` | Measured run and warmup output for N clients |
| `logs/` | Raw pgbench logs and concatenated transaction logs |
| `metrics-cN/` | Intermediate latency samples and failed log records |

For lost connections, backend failures, or distributed query failures, compare timestamps in `benchmark.log` with the per-node PostgreSQL logs. Non-empty `failed-log-records.txt` also requires investigation.

## Designing optimization experiments

Allowed optimization areas include database schema, data distribution, indexes, PostgreSQL/Citus settings, and transaction implementations, including stored procedures.

The brief gives two ways to measure individual changes:

1. **Progressive experiments:** benchmark V0, add O1 to obtain V1, add O2 to obtain V2, and continue to the final version.
2. **Ablation experiments:** benchmark the final version with each optimization removed in turn to estimate its contribution.

For each experiment, record the change, settings, results, and explanation. Claims such as “optimization X is more effective than Y” must have experimental evidence. Discuss important negative or unexpected results as well as improvements.

**Possible hypotheses to test:** merchant-based distribution may help transactions scoped to a merchant; cross-merchant transfers and global aggregation may have different bottlenecks. These are starting hypotheses, not established performance findings.

## Submission requirements

Replace `NN` with your two-digit team number.

### Result files assignment details

The Canvas **Project Result Files** assignment is worth **20 points**; the overall project brief lists **25 marks** for the project.

- **Due:** 30 October 2026 at 23:59.
- **Upload window closes:** 1 November 2026 at 23:59. This is the availability cutoff; the due date and late-submission policy still apply.
- **Submission method:** file upload.
- **Accepted file type:** ZIP.
- **Archive name:** `NN_files.zip`.
- **Top-level folder inside the archive:** `citus_project_team_NN/`.

Run this from the directory containing your team's result folder, replacing `NN` with your team number:

```bash
zip -r NN_files.zip citus_project_team_NN
```

Upload the archive to [Canvas Project Result Files](https://canvas.nus.edu.sg/courses/96671/assignments/274983).

**AI declaration:** The assignment permits AI use when clearly acknowledged, states that declaring AI use carries no penalty, and makes students responsible for the submitted content and quality. The project brief additionally requires preserved AI interactions and separate AI usage PDFs.

A declaration you can adapt to your actual use: “I used Codex to summarize the project brief and organize submission requirements. I am responsible for the content and quality of the submitted work.”

| Submission | Required name | Canvas destination |
| --- | --- | --- |
| Experiment archive | `NN_files.zip` | Project Result Files |
| Main report | `NN_report.pdf` | Project Report |
| AI usage archive, if AI was used | `NN_ai_tool.zip` | Project AI Tool Usage Files |

The experiment archive must contain `citus_project_team_NN/`, including:

- Every experiment directory named `expt_aN` or `expt_bN`.
- Each experiment's `run.sh`, `transactions/`, `slurm-results/job-<id>/`, and Slurm `citus-<job-id>.*` logs.
- `install_citus_slurm.sh`.
- `README.md` describing every experiment.

### Report assignment details

The Canvas **Project Report** assignment is worth **5 points**. Together with the result files assignment's 20 points, this matches the project total of 25 marks.

- **Due:** 30 October 2026 at 23:59.
- **Upload window closes:** 1 November 2026 at 23:59. The due date and late-submission policy still apply.
- **Submission method:** file upload.
- **Accepted file type:** PDF.
- **Filename:** `NN_report.pdf`, using your team number.

Upload the PDF to [Canvas Project Report](https://canvas.nus.edu.sg/courses/96671/assignments/274984). Include experiment identifiers in sections 2–5 so each analysis can be matched to the submitted result files.

The main report must be **at most 20 pages**, with **font size at least 10**, and include:

1. A cover page with team number, member names, and all AI tools used, or “NONE.”
2. Section 1: individual team member contributions.
3. Section 2: Task 1, baseline workload A.
4. Section 3: Task 2, optimized workload A.
5. Section 4: Task 3, baseline workload B.
6. Section 5: Task 4, optimized workload B.
7. Section 6: conclusion, lessons, and difficulties.
8. References consulted for the project.

Sections 2–5 should use experiment subsections, identify the corresponding experiment directory, and present appropriate graphs or tables. Prioritize the most important or surprising results within the page limit.

### AI tool usage assignment details

The Canvas **Project AI Tool Usage Files** assignment is worth **0 points**. Submission is required when AI use is indicated on the report cover page.

- **Due:** 30 October 2026 at 23:59.
- **Upload window closes:** 1 November 2026 at 23:59. The due date and late-submission policy still apply.
- **Submission method:** file upload.
- **Accepted file type:** ZIP.
- **Archive name:** `NN_ai_tool.zip`.
- **Contents:** at least one additional PDF, with filenames following `NN_X.pdf`, explaining how each AI tool was used for project tasks. Use descriptive text for X, such as `chatgpt_log` or `ai_tool_usage`.

For example, replace `NN` with your team number and list the PDFs you actually created:

```bash
zip NN_ai_tool.zip NN_chatgpt.pdf NN_claude.pdf NN_ai_tool_usage.pdf
```

Upload the archive to [Canvas Project AI Tool Usage Files](https://canvas.nus.edu.sg/courses/96671/assignments/274985). If no AI tool was used, no upload is required for this assignment.

**AI documentation:** If AI helped with project work, acknowledge it and preserve all interactions. Submit additional PDFs named `NN_X.pdf` explaining how each tool was used, with prompts and outputs or interaction records, zipped into `NN_ai_tool.zip`. Keep this notes interaction for that record if you use it for the project.

## Policies and evaluation

Late days are rounded up. A delay of up to one day costs 2 marks; a delay of more than one and up to two days costs 4 marks; more than two days late receives zero. The brief's example applies penalties separately to a code submission 5 hours late and a report 30 hours late, totaling 6 marks.

Evaluation considers design decisions, experimental design, interpretation, and report quality. Each team has a **20-minute Q&A session in week 13**, with **no presentation**. All members must attend; registration is announced in week 12.

## Submission progress checklist — 22 October 2026

- [x] Confirm team 14 / cs14; cluster access worked at the initial 22 October check but subsequent imports timed out with VPN disconnected.
- [x] Download and preserve the provided project files.
- [x] Configure team settings in the recorded benchmark scripts.
- [x] Verify and reuse the existing Citus installation.
- [x] Preserve `expt_a0` and `expt_b0`; retain their failure caveats.
- [x] Review A throughput, latency and failures; archive/review the complete B branch and its failure caveats.
- [ ] Finish the A/B selection: complete a115 raw import/audit and confirm choices with the A/B owners.
- [ ] Complete experiment records and preserve Codex/Claude Code interactions for the AI archive.
- [ ] Prepare the required archives and report before the deadline.

Sources: the CS4224/CS5424 Project brief, [Canvas Project Result Files assignment](https://canvas.nus.edu.sg/courses/96671/assignments/274983), [Canvas Project Report assignment](https://canvas.nus.edu.sg/courses/96671/assignments/274984), and [Canvas Project AI Tool Usage Files assignment](https://canvas.nus.edu.sg/courses/96671/assignments/274985), pasted in this chat for Semester 1, 2026/2027.
