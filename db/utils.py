"""
db/utils.py
LTO IMS — Utility helpers (plate/licence lookups used by UI dropdowns).
"""


def get_all_plate_numbers(conn, cursor):
    """Return sorted list of all plate numbers."""
    try:
        cursor.execute(
            "SELECT plateNumber FROM vehicle ORDER BY plateNumber"
        )
        return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []


def get_all_license_numbers(conn, cursor):
    """Return list of (licenseNumber, fullName) tuples, sorted by name."""
    try:
        cursor.execute(
            "SELECT licenseNumber, fullName FROM driver ORDER BY fullName"
        )
        return cursor.fetchall()
    except Exception:
        return []
