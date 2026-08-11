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
| Role | Owner | Branch |
|---|---|---|
| Team Lead / Git & LMS | | main / merges |
| Image Preprocessing (greyscale, deskew, denoise) | | feature/preprocessing |
| Table/Cell Detection | | feature/cell-detection |
| Signature Presence Detection | | feature/presence-detect |
| info.xml Parser & DB | | feature/db |
| sams.py Orchestrator | | feature/orchestrator |
| Visualization Dev 1 | | feature/infovis |
| Visualization Dev 2 | | feature/infovis-extra |
| Signature Recognition (investigate.py) | | feature/investigate |
| QA / Testing & Report | | feature/testing |

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
