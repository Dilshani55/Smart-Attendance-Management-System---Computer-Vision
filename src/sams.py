"""
sams.py - Student Attendance Management System (Image Processing)

Usage:
    python sams.py <sheet_image.jpg> <info.xml>

Pipeline:
    1. Load image
    2. Convert to greyscale
    3. Deskew / correct rotation
    4. Binarize (threshold)
    5. Locate the signature-table region and split into per-student rows
    6. Decide present/absent per row (signature = ink present)
    7. Store results in a local SQLite DB

NOTE: Steps 5-6 use a simple placeholder heuristic (ink pixel ratio in a
fixed-position row band). Replace `detect_signature_cells()` and
`is_signed()` with your team's real table/ROI detection logic
(e.g. Hough line grid detection + contour analysis) - that upgrade is
where most of the "Use of image processing techniques" marks come from.
"""

import sys
import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime

import cv2
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "attendance.db")


def log_step(message: str) -> None:
    """Print a progress message. Screenshot these for the report."""
    print(f"[sams.py] {message}")


def load_image(path: str) -> np.ndarray:
    log_step(f"Loading image: {path}")
    if not path:
        raise ValueError("Image path cannot be empty or None")
        
    if not os.path.exists(path):
        raise FileNotFoundError(f"The path does not exist: {path}")
        
    if not os.path.isfile(path):
        raise IsADirectoryError(f"The path is not a file (it is a directory): {path}")
        
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    _, ext = os.path.splitext(path.lower())
    if ext not in valid_extensions:
        raise ValueError(f"Unsupported image file format '{ext}'. Supported formats: {sorted(valid_extensions)}")
        
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not read image at {path}. The file might be corrupted or not a valid image.")
        
    if img.size == 0 or img.shape[0] == 0 or img.shape[1] == 0:
        raise ValueError(f"Loaded image has invalid dimensions: {img.shape}")
        
    return img


def to_greyscale(img: np.ndarray) -> np.ndarray:
    log_step("Converting to greyscale")
    if img is None:
        raise ValueError("Input image cannot be None")
    
    if not isinstance(img, np.ndarray):
        raise TypeError("Input image must be a numpy ndarray")
        
    if len(img.shape) == 2:
        return img.copy()
    elif len(img.shape) == 3:
        if img.shape[2] == 1:
            return img[:, :, 0].copy()
        elif img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        else:
            raise ValueError(f"Unsupported number of image channels: {img.shape[2]}")
    else:
        raise ValueError(f"Invalid image array shape: {img.shape}")


def deskew(grey: np.ndarray) -> np.ndarray:
    """Corrects rotation/perspective introduced by phone-camera capture."""
    log_step("Deskewing / correcting rotation")
    _, thresh = cv2.threshold(grey, 200, 255, cv2.THRESH_BINARY_INV)
    coords = np.column_stack(np.where(thresh > 0))
    if coords.size == 0:
        return grey
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = grey.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(grey, m, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    log_step(f"Rotation corrected by {angle:.2f} degrees")
    return rotated


def binarize(grey: np.ndarray) -> np.ndarray:
    log_step("Binarizing image")
    binary = cv2.adaptiveThreshold(
        grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 15
    )
    return binary


def denoise(binary: np.ndarray) -> np.ndarray:
    log_step("Removing noise")
    kernel = np.ones((2, 2), np.uint8)
    return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)


def parse_roster(xml_path: str):
    log_step(f"Parsing roster: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    students = []
    for s in root.findall("student"):
        students.append({
            "row": int(s.findtext("row")),
            "index": s.findtext("index"),
            "title": s.findtext("title"),
            "name": s.findtext("name"),
        })
    students.sort(key=lambda s: s["row"])
    log_step(f"Loaded {len(students)} students from roster")
    return students


def detect_signature_cells(binary: np.ndarray, num_rows: int):
    """
    PLACEHOLDER: splits the right-hand third of the image into equal
    horizontal bands, one per expected student row.

    TODO (team): replace with real table/grid detection - find the
    signature column boundaries via line detection, then crop each
    student's actual cell instead of assuming equal spacing.
    """
    log_step("Locating signature cells (placeholder row-splitting)")
    h, w = binary.shape
    sig_col_start = int(w * 0.65)
    band_height = h // max(num_rows, 1)
    cells = []
    for i in range(num_rows):
        y0 = i * band_height
        y1 = (i + 1) * band_height
        cell = binary[y0:y1, sig_col_start:w]
        cells.append(cell)
    return cells


def is_signed(cell: np.ndarray, ink_threshold: float = 0.02) -> bool:
    """A cell counts as 'signed' if enough dark ink pixels are present."""
    if cell.size == 0:
        return False
    ink_ratio = np.count_nonzero(cell) / cell.size
    return bool(ink_ratio > ink_threshold)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_index TEXT NOT NULL,
            student_name TEXT NOT NULL,
            session_date TEXT NOT NULL,
            source_image TEXT NOT NULL,
            status TEXT NOT NULL,
            processed_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_results(conn, results, session_date, image_path):
    log_step("Saving results to local database")
    processed_at = datetime.now().isoformat()
    for r in results:
        conn.execute(
            """INSERT INTO attendance
               (student_index, student_name, session_date, source_image, status, processed_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (r["index"], r["name"], session_date, image_path, r["status"], processed_at)
        )
    conn.commit()


def run(image_path: str, xml_path: str):
    students = parse_roster(xml_path)

    img = load_image(image_path)
    grey = to_greyscale(img)
    grey = deskew(grey)
    binary = binarize(grey)
    binary = denoise(binary)

    cells = detect_signature_cells(binary, len(students))

    results = []
    for student, cell in zip(students, cells):
        signed = is_signed(cell)
        status = "Present" if signed else "Absent"
        results.append({**student, "status": status})
        log_step(f"{student['name']} ({student['index']}): {status}")

    session_date = os.path.splitext(os.path.basename(image_path))[0]
    conn = init_db()
    save_results(conn, results, session_date, image_path)
    conn.close()

    log_step("Done. Results stored in attendance.db")
    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sams.py <sheet_image> <info.xml>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
