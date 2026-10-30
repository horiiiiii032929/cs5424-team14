# AI records still needed before upload

The 30 October 19:58 Singapore snapshot already includes Desmond's transcript
from merged PR #7 as `14_desmond_claude_interactions.pdf`, plus 17 recovered
Codex sessions and three local Claude sessions. Do not ask him to resend the
same supplied file. See `ai-finalization-2026-10-30.json` for verification.
The remaining completeness check concerns conversations/tools not supplied,
including any earlier detail absent from compacted exports.

The local Codex/Claude exports are a timestamped snapshot, not a complete record
of every team member's AI use. Each member (Hikaru, Kelvin, Desmond and Xincheng)
must supply or confirm:

- Every AI tool used for this project, including browser/cloud conversations.
- Prompts and visible responses or interaction records covering their project work.
- A brief account of what each tool helped with and what they checked themselves.
- Whether any project interactions are still missing. Do not infer completeness
  from a tool name being listed in another member's archive.

Use descriptive `14_X.pdf` filenames, for example `14_kelvin_chatgpt.pdf`, for
records actually supplied. Add these private files under `submission/ai/`, then
rerun `scripts/prepare_ai_archive.py` with the bundled Python runtime. That
script includes additional files already in the AI directory when building the
ZIP. Keep private records out of Git. Inspect the resulting archive before upload.

Export after final project work: the active conversation is only captured through
the moment the exporter reads it. The current export time and recovered session
inventory are in `submission/ai/session-index.json` and the generated PDFs.
Later turns and the response after an export are not automatically included.

Earlier cloud records and teammates' records cannot be reconstructed from this
Mac's local session files unless they were explicitly saved here. This remains
a team action; no completeness declaration has been made on anyone's behalf.
