"""
infovis.py - Attendance Visualization

Usage:
    python infovis.py <student_index>

Reads attendance.db (populated by sams.py) and shows a bar chart of the
given student's attendance across all processed sessions.
"""

import sys
import os
import sqlite3
import matplotlib.pyplot as plt

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "attendance.db")


def fetch_attendance(student_index: str):
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "attendance.db not found - run sams.py on at least one sheet first."
        )
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """SELECT session_date, status, student_name
           FROM attendance
           WHERE student_index = ?
           ORDER BY session_date""",
        (student_index,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def plot_attendance(student_index: str, rows):
    if not rows:
        print(f"No attendance records found for student index {student_index}")
        return

    name = rows[0][2]
    dates = [r[0] for r in rows]
    statuses = [1 if r[1] == "Present" else 0 for r in rows]
    colors = ["#2e7d32" if s == 1 else "#c62828" for s in statuses]

    present_count = sum(statuses)
    total = len(statuses)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(dates, statuses, color=colors)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Absent", "Present"])
    ax.set_title(f"Attendance Summary: {name} ({student_index})\n"
                 f"{present_count}/{total} sessions attended "
                 f"({present_count / total * 100:.1f}%)")
    ax.set_xlabel("Session (date)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python infovis.py <student_index>")
        sys.exit(1)
    idx = sys.argv[1]
    records = fetch_attendance(idx)
    plot_attendance(idx, records)
