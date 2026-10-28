# Shared report handoff to Overleaf

## Confirmed A decision

On 28 October 2026, Kelvin confirmed Hikaru's proposed selection:

- **a112 is the final A design.** Retain the matched baseline comparison and
  the seed-7/c64 warmup caveat.
- **a115 remains follow-up evidence**, with all warmup/measurement aborts and
  final-failure caveats visible.
- **a10 is a separate experiment.** It was never benchmarked on top of a112
  and is not part of the final measured A design.

This resolves A selection; it does not finalize B selection, contributions,
the bibliography or team-wide AI documentation.

## One editable report

The local LaTeX draft consolidates the existing report text and audited evidence;
it is not intended to compete with a second report in Google Docs. Kelvin
proposed moving it to Overleaf so all four members can edit together.

Once the Overleaf project is created and its link is shared, use that project
for final report edits. Keep the Google Doc as the historical draft/reference.
Use GitHub for experiment code, results, evidence and reviewed snapshots of the
Overleaf source. Avoid editing the same report independently in all three places.
Until an actual Overleaf project exists, the repo section files remain the
available working source. No Overleaf URL or invitations have been created.

## Set up the shared project

1. Sign into [NUS Overleaf](https://www.overleaf.com/edu/nus) and link the account
   to NUS SSO to claim the institutional premium features. The official NUS
   Overleaf page lists unlimited collaborators, track changes and full history.
   A normal free account allows only one collaborator per project, so use the
   institutional entitlement for this four-person team.
2. Build the current source with `bash scripts/build_report.sh`.
3. Upload `submission/14_report_overleaf.zip` as a new project, named
   **CS5424 Team 14 Final Report**. Select `main.tex` as the main document.
4. Invite Kelvin, Desmond and Xincheng using the email addresses they use for
   Overleaf, with edit access. Do not guess email addresses or enable a public
   edit link as a substitute for the intended recipients.
5. Compile and verify all figures and section files. The current local draft
   is at the 20-page limit, so shorten repeated content before adding material.
6. Share the verified project link with the team and state that it is the
   shared report. Use comments/track changes for partner review before final
   wording is accepted; GitHub branch protection does not govern Overleaf edits.
7. After the final joint review, export the source back to the repository in a
   PR and export the submission PDF as `14_report.pdf`. Do not overwrite newer
   Overleaf edits with an older repo export.

## Immediate division of work

- Hikaru and Kelvin: finalize A Sections 2-3 using the confirmed choices above.
- Desmond and Xincheng: confirm B Sections 4-5 and the B selection/attribution.
- Everyone: confirm names, contribution statements, tools used and complete AI
  interaction records; review conclusion and references.
- Report owner: export and check the final PDF (at most 20 pages including the
  cover, fonts at least 10 pt), then coordinate the three Canvas uploads.

A review draft by 29 October at 18:00 Singapore time is a proposed team target.
Official submission deadline: 30 October 2026 at 23:59 Singapore time.

Sources checked 28 October:
[NUS institutional Overleaf](https://www.overleaf.com/edu/nus),
[Overleaf free/premium plan description](https://docs.overleaf.com/getting-started/free-and-premium-plans).
