# Submission organization follow-up — 29 October 2026

The [earlier audit](non-report-audit-2026-10-29.md) is retained as a historical
review of the pre-change ZIPs. This follow-up records the authorized packaging
corrections. The report, experiment SQL, benchmark runners and measured results
are outside the edit scope.

The original user-supplied pasted overview was also located during this follow-up.
Its Sections 10–11 confirm the raw-log/CSV structure, experiment folder contents,
root name, installer/README and the separate AI-PDF ZIP submission. The inherited
copies remain explicitly classified as supporting material, not measured results
of b203/b204.

## Changes applied

- Kept all 23 experiment IDs/paths to preserve references. Marked b203/b204 as
  unbenchmarked source variants with inherited b2/job-928583 evidence; marked
  b201/job-918781 as inherited b0 evidence. These copies are not independent runs.
- Added all six omitted supporting evidence trees: read-only correctness,
  join-placement correctness, scalable-validator checks, read-only pilots,
  join-placement pilots and historical local-native results (355 files).
- Added a map for all 45 unique jobs, their canonical experiment, copied paths
  and exact preserved source matches for the 184 recorded runtime file hashes.
- Added clear cluster and b6 correctness-harness entry points. Labelled the
  archived analysis scripts as repository utilities and identified the exact
  repository revision/layout needed to use them.
- Replaced only the packaged installer's notification directive with the team's
  already configured value; retained the original installer in a source snapshot.
- Replaced stale package-level review language with factual experiment and
  evidence descriptions. A remains a112, a115 a follow-up, and a10 separate.
  No decision was made on behalf of the B owners.
- Added separate original-source and final-destination provenance hashes.
- Refreshed locally recoverable AI interactions and rebuilt the private AI ZIP.

The result package still has 48 job paths representing 45 jobs. The additional
evidence contains local checks and pilots, not new Slurm performance results.
Original abort/failure evidence remains intact. No benchmark was rerun.

## Verification

The rebuilt result ZIP contains 5,664 files; all 5,663 manifest hashes match.
Both ZIPs match their staging directories and pass decompression/CRC checks.
All original experiment source and result bytes are unchanged at their paths;
the starter installer is additionally preserved in its source snapshot. All 184
runtime source hashes still resolve. Every one of the 355 added evidence files
matches its original. Running the organizer again produces identical content.
The report sources, report PDF and Overleaf source ZIP retain their original hashes.

The AI snapshot contains 11 Codex and 3 Claude Code sessions. Its 46-page Codex
and 23-page Claude PDFs parse without empty pages; sampled rendered pages are
readable. The credential scan found no known local credential values or matched
token patterns. This is a bounded check and does not certify team-wide record
completeness. The current conversation remains captured only through export time.

## Remaining actions

1. Obtain any missing earlier/cloud interactions and teammates' records using
   [the AI checklist](AI_RECORDS_NEEDED.md). Local regeneration cannot establish
   team-wide completeness. Refresh again after final work, before upload.
2. Keep the existing runtime-source limitation explicit: 30 of 45 jobs have no
   runtime hash manifest. Readback hashes cannot retroactively replace it.
3. The team still needs to complete the separate final report review, ensure its
   experiment descriptions agree with these labels, upload all three required
   files and verify the receipts. This work did not edit the report or upload.

The old ZIPs are preserved privately in `_build/before-organization-20261029/`.
Current ZIPs are in `upload/`. Verification results for the organization are in
`organization-validation-2026-10-29.json`; earlier audit measurements remain in
their original audit files and are not overwritten.
