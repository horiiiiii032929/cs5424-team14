#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
report_root="$repo_root/submission/report"
build_root="$repo_root/submission/_build/report-build"
upload_root="$repo_root/submission/upload"
mkdir -p "$build_root" "$upload_root"
cd "$report_root"
if command -v tectonic >/dev/null 2>&1; then
  tectonic --outdir "$build_root" main.tex
elif command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$build_root" main.tex
else
  echo 'Install Tectonic or latexmk, or import submission/report/ into Overleaf.' >&2
  exit 1
fi
cp "$build_root/main.pdf" "$upload_root/14_report.pdf"
# Python's standard library is sufficient for the portable Overleaf archive.
python3 - "$report_root" "$repo_root/submission/14_report_overleaf.zip" <<'PY'
from pathlib import Path
import sys,zipfile
root=Path(sys.argv[1])
with zipfile.ZipFile(sys.argv[2],'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.suffix in {'.tex','.pdf','.md'}:
            archive.write(path,path.relative_to(root))
print('Overleaf source:',sys.argv[2])
PY
echo "Report: $upload_root/14_report.pdf"
echo 'Check the rendered PDF: at most 20 pages including cover, minimum 10-point text.'
