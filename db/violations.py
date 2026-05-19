"""
db/violations.py
LTO IMS — Violation CRUD operations.
"""

from db.helpers import _parse_date


def add_violation_db(conn, cursor, vio_id, license_number, plate,
                     status, vtype, location, vio_date, fine, officer):
    """
    Inserts into violation + violation_date in a single transaction.
    officer may be None (column is nullable in schema).
    """
    try:
        cursor.execute(
            "SELECT violationId FROM violation WHERE violationId = %s",
            (vio_id,)
        )
        if cursor.fetchone():
            return False, "Error: Violation ID already exists."

        cursor.execute("""
            INSERT INTO violation
                (violationId, licenseNumber, plateNumber, status, type,
                 location, violationDate, fineAmount, apprehendingOfficer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (vio_id, license_number, plate, status, vtype,
              location, vio_date, fine, officer or None))

        # Populate violation_date dimension table
        d = _parse_date(vio_date)
        cursor.execute("""
            INSERT INTO violation_date
                (violationId, violationDate, month, day, year)
            VALUES (%s, %s, %s, %s, %s)
        """, (vio_id, vio_date, d.month, d.day, d.year))

        conn.commit()
        return True, "Violation recorded successfully."
    except Exception as e:
        conn.rollback()
        if e.args[0] == 1452:
            return False, "Error: License number or plate number does not exist."
        return False, f"Database error: {e}"


def get_violations_db(conn, cursor, criteria=None):
    """
    Rows: (violationId, licenseNumber, fullName, plateNumber, status,
           type, location, violationDate, fineAmount, apprehendingOfficer)
    """
    query = """
        SELECT vi.violationId, vi.licenseNumber, d.fullName,
               vi.plateNumber, vi.status, vi.type,
               vi.location, vi.violationDate, vi.fineAmount,
               vi.apprehendingOfficer
        FROM violation vi
        JOIN driver d ON vi.licenseNumber = d.licenseNumber
    """
    params, filters = [], []

    if criteria:
        if criteria.get("licenseNumber"):
            filters.append("vi.licenseNumber = %s")
            params.append(criteria["licenseNumber"])
        if criteria.get("plateNumber"):
            filters.append("vi.plateNumber LIKE %s")
            params.append(f"%{criteria['plateNumber']}%")
        if criteria.get("status"):
            filters.append("vi.status = %s")
            params.append(criteria["status"])
        if criteria.get("date_from"):
            filters.append("vi.violationDate >= %s")
            params.append(criteria["date_from"])
        if criteria.get("date_to"):
            filters.append("vi.violationDate <= %s")
            params.append(criteria["date_to"])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY vi.violationDate DESC"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def edit_violation_db(conn, cursor, vio_id, updates):
    try:
        cursor.execute(
            "SELECT violationId FROM violation WHERE violationId = %s",
            (vio_id,)
        )
        if not cursor.fetchone():
            return False, "Error: Violation not found."

        set_clause = ", ".join(f"{k} = %s" for k in updates)
        cursor.execute(
            f"UPDATE violation SET {set_clause} WHERE violationId = %s",
            list(updates.values()) + [vio_id]
        )
        conn.commit()
        return True, "Violation updated successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_violation_db(conn, cursor, vio_id):
    """Deletes violation + cascades to violation_date (ON DELETE CASCADE in schema)."""
    try:
        cursor.execute(
            "SELECT violationId FROM violation WHERE violationId = %s",
            (vio_id,)
        )
        if not cursor.fetchone():
            return False, "Error: Violation not found."

        cursor.execute(
            "DELETE FROM violation WHERE violationId = %s", (vio_id,)
        )
        conn.commit()
        return True, "Violation deleted successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
