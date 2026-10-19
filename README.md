# PDF-to-TXT Extractor

**Python CLI for extracting PDF text, with page-level OCR fallback.**  
[Source](https://github.com/kernelkeruv/PDF-to-TXT-Extractor/blob/main/extract_to_txt.py) · [Security policy](SECURITY.md)

## Security use case

Extract searchable text from documents received for authorized review, research, and forensic triage. The script extracts the embedded text layer on each page; if that page has no text, it renders the page and sends it to local Tesseract OCR. It writes a UTF-8 text derivative and leaves the input PDF unchanged.

**Limitations:** This is *not* a forensic acquisition tool. It does not preserve layout, attachment metadata, PDF signatures, timestamps, or chain of custody. OCR accuracy is not guaranteed; pages that already contain some embedded text will not be OCR'd. Errors on individual pages are written to the output text. Preserve and hash originals separately before processing evidence. Never treat output text alone as an authentic original.

## Requirements

- Python 3.11, with packages from [requirements.txt](requirements.txt).
- Tesseract OCR on PATH for raster/image-only PDF pages; it is not needed for text-layer extraction.
- Sufficient temporary disk space and memory for rendering large scanned pages.
- Supported example environments: Windows with PowerShell or Linux with Bash. The existing Windows `setup.ps1` is optional, may install packages and edit a PowerShell profile, and should be **reviewed before execution**. Prefer the explicit virtual-environment steps below.

## Reproduce a working example (Linux / Bash)

Set `WORK_DIR` to a writable directory you control before running. The commands below create only a synthetic demonstration PDF, so no personal records are used.

```bash
set -Eeuo pipefail
: "${WORK_DIR:?Set WORK_DIR to an existing writable directory}"
git clone https://github.com/kernelkeruv/PDF-to-TXT-Extractor.git "$WORK_DIR/PDF-to-TXT-Extractor"
cd "$WORK_DIR/PDF-to-TXT-Extractor"
python3.11 -m venv "$WORK_DIR/pdf-to-txt-venv"
"$WORK_DIR/pdf-to-txt-venv/bin/python" -m pip install -r requirements.txt
"$WORK_DIR/pdf-to-txt-venv/bin/python" -m unittest discover -s tests -v
"$WORK_DIR/pdf-to-txt-venv/bin/python" - <<'PY'
import os
from pathlib import Path
import fitz
work = Path(os.environ["WORK_DIR"])
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "SYNTHETIC PDF TEST RECORD")
doc.save(work / "synthetic-demo.pdf")
doc.close()
PY
"$WORK_DIR/pdf-to-txt-venv/bin/python" extract_to_txt.py \
  --pdf "$WORK_DIR/synthetic-demo.pdf" \
  --output "$WORK_DIR/synthetic-demo.txt"
grep -F 'SYNTHETIC PDF TEST RECORD' "$WORK_DIR/synthetic-demo.txt"
sha256sum "$WORK_DIR/synthetic-demo.pdf" "$WORK_DIR/synthetic-demo.txt"
```

**Expected verification:** the unit tests pass, the `grep` command prints `SYNTHETIC PDF TEST RECORD`, and the SHA-256 command prints one checksum for each file. These are expected checks, *not* claims of completed testing on your machine.

For image-only pages, install the `tesseract` executable separately and check `tesseract --version`. An installed `pytesseract` Python library by itself does not install the OCR engine.

## Windows / PowerShell

From a checked-out repository, create a Python 3.11 virtual environment and install the pinned dependencies:

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe .\extract_to_txt.py --pdf $InputPdf --output $OutputTxt
```

Set `$InputPdf` and `$OutputTxt` to full paths first. Verify `Get-FileHash -Algorithm SHA256 -LiteralPath $InputPdf` before conversion. Do not use real evidence to test installation.

## Implementation and reproducibility

- `extract_to_txt.py`: `--pdf` input and `--output` output; processes pages sequentially with a progress bar.
- `tests/test_extract.py`: synthetic text-layer PDF and mocked OCR fallback tests; no confidential fixtures and no live network traffic.
- `requirements.txt`: currently pinned dependency versions; test against your target Python platform before changing versions.
- `setup.ps1` and `launch.ps1`: legacy optional Windows helpers, not required for the Python CLI above.

## Responsible use

Handle source files as untrusted content, run in a least-privilege environment, and verify the resulting output before downstream analysis. Exclude originals, transcripts, OCR outputs, personal data, tokens, and generated evidence bundles from public commits.
