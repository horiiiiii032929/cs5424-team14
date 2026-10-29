# Non-report reconciliation — 30 October 2026

Xincheng's commit `1a5a2f3e380eb93dd8840ec51a34d388c160c49d` removes unused
b202, b203 and b204. The package builder previously would have reintroduced them
from the older cluster readback. It now excludes both their submitted names and
original cluster aliases across repository, archive and remote imports. The
finalizer rejects stale staging trees containing them instead of silently
publishing an outdated archive.

The current package has **20 experiment folders, 44 job paths and 43 distinct
Slurm jobs**, plus eight separately identified local-only implementations.
b201/job-918781 remains explicitly inherited from b0. b203/b204's inherited
b2 results are no longer presented as separate experiment evidence. Original
readbacks and the prior complete package remain in private build storage.
The 29 October audits describe their historical archive and are not overwritten.

All 1,771 incoming B files matched previously preserved evidence. The selected
b0 runner includes the already-read-back zero-weight fix: `add_workload` returns
success for a disabled transaction, allowing T6-only/T7-only configurations
under `set -e`. Its previous runner is retained in
`expt_b0/source_snapshots/pre-zero-weight-fix/`. b6's SQL change adds a comment;
its correctness harness is now directly available in `expt_b6/`. Instructions
use that directory. Measured results, failed records and phase exits are not
rewritten, and no new cluster benchmark is claimed.

Validation checks every final checksum against the ZIP, every provenance
record against its destination, all 184 runtime source hashes across 15 jobs,
and byte preservation of retained original shell/SQL/result files. All 975
root-level B files from the older PR #2 are already represented byte-for-byte.
The current B files are checked against their submitted paths, allowing only
README packaging notes. The original 71 packaged shell scripts pass the
cluster's Bash 5.2 parser; the added historical runner had passed the previous
archive audit. The macOS Bash 3 parser cannot parse the runners' existing `-v`
conditional; cluster Bash is the relevant interpreter.

The report source, report PDF and Overleaf ZIP are unchanged. Exact validation
counts and archive hashes are recorded in `reconciliation-validation-2026-10-30.json`
and `validation.json`.

Available local AI exports were refreshed: 12 Codex and 3 Claude Code sessions,
with 50- and 23-page PDFs respectively. ZIP integrity, record counts, readable
text, sampled rendered pages and known credential redaction were checked.
These are a timestamped snapshot, not a claim of team-wide completeness.
Teammates' missing AI records and earlier cloud conversations still require
their actual exports. No Canvas upload has been performed.

Generated ZIPs and private AI records are ignored by Git. They are available
locally under `submission/upload/`; cloning the repository alone does not
retrieve those upload files. Previous ZIPs and staging files are preserved at
`submission/_build/before-reconcile-20261030/`.
