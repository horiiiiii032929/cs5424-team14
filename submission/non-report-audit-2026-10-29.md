# Non-report submission audit — 29 October 2026

**Verdict: the core cluster-code/result structure passes, but the non-report submission is not yet fully ready.** The remaining issues concern AI record completeness, experiment attribution, omitted supporting evidence and reproduction instructions. No report source or report PDF was reviewed or changed in this audit.

The review used the saved course description in `PROJECT_NOTES.md`, the supplied-overview mapping in `submission/assignment-requirements.md`, the actual ZIP contents, local source/evidence and a fresh read-only cluster inventory at approximately 22:18–22:25 Singapore time. The original Canvas page was not independently reread in this audit, so later instructor changes remain outside its scope.

## Findings requiring attention

### 1. AI interaction archive is incomplete

The existing `14_ai_tool.zip` contains the expected two interaction PDFs, usage index, session index and JSONL records. It represents nine Codex and three Claude Code sessions. Its generation timestamp is **29 October, 14:05 Singapore time**. Two newer project conversations, including this audit conversation, are absent; the last exported conversation also stops before that conversation's final response. Two other nonexported sessions are automated approval reviews and were correctly excluded.

The archive itself explicitly says earlier cloud/ChatGPT interactions and teammates' records have not been established as complete. Therefore it cannot yet satisfy the requirement to preserve all project AI interactions. Refresh the locally recoverable records after final work, collect each member's missing records/tools, and inspect the refreshed archive. The current session-index record counts are internally consistent. Both PDFs parse without empty pages, and sampled rendered pages are readable. No known `.env` credential values or token-shaped secrets were found by the bounded archive scan; that is not a guarantee against every possible secret format.

### 2. b203/b204 are not independently benchmarked experiments

`expt_b203/slurm-results/job-928583/` and `expt_b204/slurm-results/job-928583/` contain the same original job as `expt_b2`. The logged pgbench commands explicitly point to **expt_b2/transactions**, not to either supplementary design. Neither supplementary folder has another job in the current cluster inventory.

The current archive README calls these a T6 control and covering-index control and lists the copied job without explicitly explaining this at each entry. The broad claim of “23 Slurm experiments” can therefore be read as 23 separately measured designs. Preserve the copied evidence, but label these two as unbenchmarked supporting source variants with inherited b2 evidence, or relocate their implementations into supporting materials and keep the original job under b2. Do not describe the copied measurements as results of b203/b204. Likewise, b201's copy of baseline job 918781 must remain identified as inherited b0 evidence; b201 also has its own later jobs.

### 3. Some supporting correctness/pilot evidence is omitted

The packaging allowlist in `scripts/prepare_submission.py` omits these existing local directories:

| Directory under `results/` | Local files | In packaged `evidence/local-only/`? |
|---|---:|---|
| `correctness-readonly-20261019` | 32 | No |
| `correctness-join-placement-20261019` | 35 | No |
| `scalable-validator-checks-20261019` | 13 | No |
| `readonly-pilot-20261019` | 50 | No |
| `join-placement-pilot-20261019` | 18 | No |
| `local-native-20261014` | 207 | No |

Some individual bytes are duplicated elsewhere, but these complete evidence trees are absent. This matters because the included `evidence/local-only/followup-20261019/README.md` describes 151 follow-up correctness checks and links to the omitted read-only/join-placement suites. Add the relevant supporting suites with their classification intact and provide working packaged paths. The historical `local-native` suite is lower priority if it is intentionally excluded; document that exclusion. These are **supporting local results**, not missing course-cluster jobs.

### 4. Bundled analysis helpers are not standalone reproduction tools

`analysis_scripts/local_experiments.py` resolves its root to the extracted `citus_project_team_14/` directory, then expects a second nested `citus_project_team_14/`, `compose.yaml`, and other repository assets that are not at those locations in the ZIP. `check_correctness.py` imports and inherits that layout. Packaging/build helpers also assume the original repository tree.

The individual top-level cluster experiments have the required transaction files and literal SCRIPT_DIR dependencies, so this is not a demonstrated failure of their `sbatch run.sh` entry points. Either supply a working helper layout/wrapper and dependencies, or clearly label the helpers as archived repository utilities and give the repository checkout/location needed to use them. Do not imply they run directly from the extracted archive. Explain how to invoke the separately archived b6 correctness harness as well.

### 5. Installer still has the starter notification address

The packaged `install_citus_slurm.sh` contains `alice_and_bob@u.nus.edu`. The live team's installer differs only in that notification directive and has a configured team member address. Preserve historical originals, but use or document the configured installer for a runnable submission. Eight top-level Hikaru experiment scripts explicitly disable mail notifications; this does not prevent execution, but differs from the setup guidance to configure email.

### 6. Submission metadata needs reconciliation

The ZIP README still describes A selection as awaiting confirmation. The local handoff already records a112 as selected. B selection is left as pending in the ZIP; reconcile it with the B owners' actual decision. Remove stale review instructions from the final archive README, without altering historical experimental logs.

`packaging-provenance.json` has 22 entries whose original-source hashes no longer match the destination README bytes, because packaging notes were appended. `checksums.sha256` correctly hashes the final files. Clarify that provenance records the pre-edit source, or store separate source/final hashes; otherwise a downstream provenance verifier will report unexplained mismatches.

## Checks that passed

| Check | Result |
|---|---|
| Result ZIP integrity | All 5,305 file entries decompressed; no duplicate/unsafe member paths |
| Archive root | Exactly one `citus_project_team_14/` root |
| Final checksums | All 5,304 listed file hashes match; no unlisted content except the checksum file itself |
| ZIP versus local staging | Exact file coverage and byte agreement for result and AI archives |
| Top-level experiment layout | All 23 folders match `expt_[ab]N`; each has `run.sh`, README, nine correctly named transaction SQL files and Slurm results |
| Slurm output/error pairs | Both files present for every one of 48 job paths |
| Job identity | 45 distinct Slurm IDs; 918781 occurs twice and 928583 occurs three times |
| Local-only implementation separation | Eight a103–a110 supporting implementations stored separately |
| Team/workload defaults | All 23 top-level runners default to team 14; A/B workload defaults agree with their names |
| Shell syntax | All 75 packaged shell files pass `bash -n` with the cluster's Bash 5.2; 101 live shell files also pass |
| Python syntax | Packaged Python files parse successfully; this does not test imports or runtime dependencies |
| Direct cluster-script dependencies | Required transaction names and literal SCRIPT_DIR file references exist |
| Metrics | All 175 CSV case rows agree with raw transaction counts, successful TPS, mean/p50/p95/p99, per-transaction counts/latencies and textual retry/failure totals |
| Recorded measurement exits | Every summary exit agrees with its result-file exit marker |
| Live cluster coverage | All experiment shell/SQL code and all Slurm-job file contents in the shared project and three recorded Hikaru deployments are represented in the archive |
| Runtime source hashes | All 184 recorded file hashes from 15 jobs resolve to preserved packaged bytes |
| AI ZIP structure | 17 files; descriptive Team-14 PDF names, two tool records, index and supplemental JSONL |

Live coverage is based on SHA-256 content matching, including documented aliases and snapshots. It does not mean identical current paths. The three live shared-project files not represented byte-for-byte are the configured installer and its two installation logs; installation output logs are not explicitly required in the saved brief. Other uncovered deployment files are old documentation, repository utilities and omitted local-test evidence, not new course-cluster experiment outputs.

## Evidence limitations that must remain visible

- There are **157 unique job/client measurement cases** after removing copied jobs. Of these, 39 record nonzero measurement exits, 26 have explicitly nonzero warmup exits and 29 contain failed transaction log records. These categories overlap. Counts are across historical, diagnostic, full and supplementary runs; they are not the failure rate of one final design.
- 97 unique cases have explicit zero warmup and measurement exits and zero failed raw records. This describes phase completion, not proof of transaction correctness or equal experimental conditions.
- Two early b6/c1 cases (956642 and 956776) have no warmup exit footer. Do not infer success from absence of that marker.
- Six jobs have no measured summary rows: 967193, 988728, 988782, 988729, 988800 and 1031165. They are preserved early/failed attempts. Five lack summary/config/transaction CSVs; 1031165 has an empty measurement summary. Do not manufacture missing metrics.
- Only 15 of 45 distinct jobs have runtime code-hash manifests. The other 30 have source/log evidence but no runtime hash certification. Fresh readback hashes cannot retroactively prove their execution-time source.
- Four old A cases use an earlier `sql/verify.sql` than their current top-level folder: a101/977433, a101/977468, a111/977434 and a112/977435. The exact old validator is preserved in the corresponding historical source snapshots. An explicit job-to-source map would make reproduction clearer.
- Quantiles were checked using the supplied runner's lower order statistic: index `floor((n-1)*q)` in a zero-based sorted list. A different percentile convention yields different values and is not evidence of corrupt output.
- The scripts use configured duration for successful TPS, including aborted measurements. A numerically correct summary does not make an aborted run eligible for a clean performance comparison.

## Per-experiment inventory

See [the complete experiment table](audit-2026-10-29-experiments.csv). It lists job paths, measurement rows, warmup aborts, measurement aborts, cases with failed records and runtime-manifest coverage for every top-level experiment. Duplicate inherited jobs are intentionally visible in this table and must not be counted as independent experiments.

The compact verification record is [audit-2026-10-29.json](audit-2026-10-29.json). Detailed local/remote manifests, per-case calculations, read-only audit code and rendered AI samples are retained privately under `submission/_build/audit-20261029/`.

This was a read-only review of existing code, evidence and packages. No benchmarks or database mutations were executed, no installation was changed, no uploads were made, and no source/result/AI archive was overwritten. SQL behavior under all possible inputs/concurrent schedules was not exhaustively re-tested. The audit does not certify code correctness solely from matching logs or passing syntax checks.
