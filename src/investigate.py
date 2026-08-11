"""
investigate.py - Signature Recognition / Verification (bonus feature)

Usage:
    python investigate.py <student_index>

Collects every signed instance of a student's signature crop across all
processed sheets and compares them pairwise to flag signatures that look
like they came from a different person (i.e. possible proxy-signing).

This is a starter skeleton using simple ORB feature matching, which is
enough to demonstrate the technique. For higher marks, the team can
upgrade the comparison step to a trained model or a more robust
handwriting-similarity method, and cite the technique in the report.
"""

import sys
import os
import glob
import cv2
import numpy as np

SIGNATURE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "signatures")


def load_signature_crops(student_index: str):
    """
    Expects pre-cropped signature images saved by sams.py (or manually)
    under data/signatures/<student_index>/*.png
    """
    folder = os.path.join(SIGNATURE_DIR, student_index)
    paths = sorted(glob.glob(os.path.join(folder, "*.png")))
    if not paths:
        print(f"No signature crops found in {folder}")
        print("TODO: update sams.py to save each detected signature crop there.")
    return [(p, cv2.imread(p, cv2.IMREAD_GRAYSCALE)) for p in paths]


def similarity_score(img1: np.ndarray, img2: np.ndarray) -> float:
    """Returns a 0-1 similarity score using ORB descriptor matching."""
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None or len(kp1) == 0 or len(kp2) == 0:
        return 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    if not matches:
        return 0.0

    good_matches = [m for m in matches if m.distance < 50]
    return len(good_matches) / max(len(kp1), len(kp2))


def investigate(student_index: str, threshold: float = 0.3):
    crops = load_signature_crops(student_index)
    if len(crops) < 2:
        print("Need at least 2 signature samples to compare.")
        return

    print(f"Comparing {len(crops)} signature samples for student {student_index}")
    flagged = []
    for i in range(len(crops)):
        for j in range(i + 1, len(crops)):
            (path_a, img_a), (path_b, img_b) = crops[i], crops[j]
            score = similarity_score(img_a, img_b)
            match = "MATCH" if score >= threshold else "MISMATCH (flagged)"
            print(f"  {os.path.basename(path_a)} vs {os.path.basename(path_b)}: "
                  f"score={score:.2f} -> {match}")
            if score < threshold:
                flagged.append((path_a, path_b, score))

    if flagged:
        print(f"\n{len(flagged)} pair(s) flagged as possible mismatched signatures.")
    else:
        print("\nAll signature samples appear consistent.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python investigate.py <student_index>")
        sys.exit(1)
    investigate(sys.argv[1])
