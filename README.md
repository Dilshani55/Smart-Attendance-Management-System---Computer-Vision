# SAMS - Student Attendance Management System
CS402.3 Computer Graphics & Visualization — Group Coursework

## Setup
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Project Structure
```
sams-project/
├── src/
│   ├── sams.py         # Image processing: sign-sheet -> present/absent -> DB
│   ├── infovis.py      # Attendance visualization for one student
│   └── investigate.py  # Signature verification (bonus)
├── data/
│   ├── info.xml         # Sample student roster
│   └── sheets/          # Put the 5 signing sheet images here
├── tests/
│   └── test_sams.py     # Pytest smoke tests
├── report/               # Word report + screenshots go here
├── requirements.txt
└── attendance.db          # Created automatically after first run
```

## Running
```bash
# 1. Put a signing sheet image in data/sheets/, e.g. data/sheets/10.07.2019.jpg
cd src
python sams.py ../data/sheets/10.07.2019.jpg ../data/info.xml

# 2. See a student's attendance chart
python infovis.py 10000409

# 3. (Bonus) Verify signature consistency
python investigate.py 10000409
```

## Team Roles (10 members)
| # | Member | Owner | Owns (file/function) | What they actually code | Branch |
|---|---|---|---|---|---|
| 1 | **Dev 1 (You)** | | `sams.py` -> `load_image()`, `to_greyscale()` | Image loading + greyscale conversion, error handling for bad file paths | `feature/preprocessing` |
| 2 | **Dev 2** | | `sams.py` -> `deskew()` | Rotation correction (minAreaRect-based deskew), test on all 5 sheets | `feature/deskew` |
| 3 | **Dev 3** | | `sams.py` -> `binarize()`, `denoise()` | Adaptive thresholding + morphological noise removal, tune parameters | `feature/binarize-denoise` |
| 4 | **Dev 4** | | `sams.py` -> `detect_signature_cells()` | Replace placeholder row-split with real table/grid detection (Hough lines or contour-based cell boundaries) | `feature/cell-detection` |
| 5 | **Dev 5** | | `sams.py` -> `is_signed()` | Ink-pixel ratio / contour-count logic to decide present vs absent per cell, calibrate threshold | `feature/presence-detect` |
| 6 | **Dev 6** | | `sams.py` -> `parse_roster()`, `init_db()`, `save_results()` | info.xml parsing + SQLite schema + saving attendance records | `feature/db` |
| 7 | **Dev 7** | | `sams.py` -> `run()` (orchestrator) + logging | Wires everyone's functions together into the CLI tool, adds clear step-by-step console output for report screenshots | `feature/orchestrator` |
| 8 | **Dev 8** | | `infovis.py` | Per-student attendance bar chart — extend with colors, percentage labels, session labels | `feature/infovis` |
| 9 | **Dev 9** | | `infovis.py` extra + testing | Overall class summary chart (all 6 students, all 5 sessions) + runs `sams.py` against all 5 real sheets, logs results/errors | `feature/infovis-extra` |
| 10 | **Dev 10** | | `investigate.py` | ORB signature comparison logic (bonus feature) + saving signature crops from Dev 4's cell detection | `feature/investigate` |

## Workflow
1. Each member works on their own `feature/*` branch.
2. Commit early and often under your own name/email — **individual marks depend on this**.
3. Open a Pull Request into `main` when a piece is working; Team Lead reviews and merges.
4. Run `python -m pytest tests/` before merging to catch regressions.

## Current Status
This is a starter skeleton:
- `sams.py` has real greyscale/deskew/binarize/denoise steps working.
- Signature-cell detection in `sams.py` is a **placeholder** (equal row-splitting) — replace with real grid/contour detection for full marks.
- `infovis.py` is functional once `attendance.db` has data.
- `investigate.py` needs signature crops saved to `data/signatures/<index>/` (not yet wired into `sams.py` — add this as part of the cell-detection upgrade).
