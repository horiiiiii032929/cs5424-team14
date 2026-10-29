#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
report_root="$repo_root/submission/report"
build_root="$repo_root/submission/_build/report-build"
upload_root="$repo_root/submission/upload"
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != '--source-only' ) ]]; then
  echo 'Usage: bash scripts/build_report.sh [--source-only]' >&2
  exit 2
fi
mkdir -p "$build_root" "$upload_root"
# Package a portable project: no old Markdown drafts, private files or build cache.
python3 - "$report_root" "$repo_root/submission/14_report_overleaf.zip" <<'PY'
from pathlib import Path
import sys, zipfile
root = Path(sys.argv[1])
required = ['main.tex', 'metadata.tex', 'report-style.tex', 'references.bib', 'README.md']
files = [root / name for name in required]
files += sorted((root / 'sections').rglob('*.tex'))
files += sorted((root / 'images').glob('*.pdf'))
for source in files:
    if not source.is_file():
        raise SystemExit(f'Missing report source: {source}')
with zipfile.ZipFile(sys.argv[2], 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(root))
with zipfile.ZipFile(sys.argv[2]) as archive:
    if archive.testzip() is not None:
        raise SystemExit('The source ZIP failed its integrity check.')
print('Overleaf source:', sys.argv[2])
PY
if [[ "${1:-}" == '--source-only' ]]; then
  exit 0
fi
cd "$report_root"
if command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs --keep-intermediates --outdir "$build_root" main.tex
elif command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$build_root" main.tex
else
  echo 'Install Tectonic or latexmk, or import submission/report/ into Overleaf.' >&2
  exit 1
fi
cp "$build_root/main.pdf" "$upload_root/14_report.pdf"
echo "Report: $upload_root/14_report.pdf"
echo 'Check the rendered PDF: at most 20 pages including cover, minimum 10-point text.'
