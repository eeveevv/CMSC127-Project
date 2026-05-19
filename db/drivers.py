"""
db/drivers.py
LTO IMS — Driver & Driver Address CRUD operations.
"""

from db.helpers import _calc_age, _parse_date


# ─────────────────────────────────────────────
# DRIVER CRUD
# ─────────────────────────────────────────────

def add_driver_db(conn, cursor, license_number, full_name, license_status,
                  license_type, issuance_date, expiration_date, dob, sex):
    """Insert a new driver row. Returns (bool, message)."""
    try:
        dob_date = _parse_date(dob)
        age = _calc_age(dob_date)

        cursor.execute(
            "SELECT licenseNumber FROM driver WHERE licenseNumber = %s",
            (license_number,)
        )
        if cursor.fetchone():
            return False, "Error: License number already exists."

        cursor.execute("""
            INSERT INTO driver
                (licenseNumber, fullName, licenseStatus, licenseType,
                 licenseIssuanceDate, licenseExpirationDate,
                 dateOfBirth, age, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (license_number, full_name, license_status, license_type,
              issuance_date, expiration_date, dob, age, sex))
        conn.commit()
        return True, f"Driver '{full_name}' added successfully."
    except ValueError:
        conn.rollback()
        return False, "Error: Invalid date format. Use YYYY-MM-DD."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"


def get_drivers_db(conn, cursor, criteria=None):
    """
    Fetch drivers with optional filter criteria dict.
    Returns (True, rows) or (False, error_string).
    Rows: (licenseNumber, fullName, licenseStatus, licenseType,
           licenseIssuanceDate, licenseExpirationDate,
           dateOfBirth, age, sex, address, city, region)
    """
    query = """
        SELECT d.licenseNumber, d.fullName, d.licenseStatus, d.licenseType,
               d.licenseIssuanceDate, d.licenseExpirationDate,
               d.dateOfBirth, d.age, d.sex,
               da.address, da.city, da.region
        FROM driver d
        LEFT JOIN driver_address da ON d.licenseNumber = da.licenseNumber
    """
    params, filters = [], []

    if criteria:
        if criteria.get("licenseNumber"):
            filters.append("d.licenseNumber = %s")
            params.append(criteria["licenseNumber"])
        if criteria.get("fullName"):
            filters.append("d.fullName LIKE %s")
            params.append(f"%{criteria['fullName']}%")
        if criteria.get("licenseType"):
            filters.append("d.licenseType = %s")
            params.append(criteria["licenseType"])
        if criteria.get("licenseStatus"):
            filters.append("d.licenseStatus = %s")
            params.append(criteria["licenseStatus"])
        if criteria.get("sex"):
            filters.append("d.sex = %s")
            params.append(criteria["sex"])
        if criteria.get("age_min") is not None:
            filters.append("d.age >= %s")
            params.append(criteria["age_min"])
        if criteria.get("age_max") is not None:
            filters.append("d.age <= %s")
            params.append(criteria["age_max"])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY d.fullName"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def edit_driver_db(conn, cursor, license_number, updates):
    """
    Update mutable driver fields.
    If dateOfBirth is in updates, age is recalculated automatically.
    """
    try:
        cursor.execute(
            "SELECT licenseNumber FROM driver WHERE licenseNumber = %s",
            (license_number,)
        )
        if not cursor.fetchone():
            return False, "Error: Driver not found."

        db_updates = {}
        for k, v in updates.items():
            if k == "dateOfBirth":
                dob = _parse_date(v)
                db_updates["dateOfBirth"] = v
                db_updates["age"] = _calc_age(dob)
            else:
                db_updates[k] = v

        if not db_updates:
            return False, "No changes provided."

        set_clause = ", ".join(f"{k} = %s" for k in db_updates)
        cursor.execute(
            f"UPDATE driver SET {set_clause} WHERE licenseNumber = %s",
            list(db_updates.values()) + [license_number]
        )
        conn.commit()
        return True, "Driver updated successfully."
    except ValueError:
        conn.rollback()
        return False, "Error: Invalid date format. Use YYYY-MM-DD."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_driver_db(conn, cursor, license_number):
    """Delete a driver (cascades to driver_address; restricted by vehicle/violation FKs)."""
    try:
        cursor.execute(
            "SELECT fullName FROM driver WHERE licenseNumber = %s",
            (license_number,)
        )
        row = cursor.fetchone()
        if not row:
            return False, "Error: Driver not found."

        cursor.execute(
            "DELETE FROM driver WHERE licenseNumber = %s",
            (license_number,)
        )
        conn.commit()
        return True, f"Driver '{row[0]}' deleted successfully."
    except Exception as e:
        conn.rollback()
        if e.args[0] == 1451:
            return False, "Cannot delete: driver has linked vehicles or violations."
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# DRIVER ADDRESS
# ─────────────────────────────────────────────

def upsert_driver_address_db(conn, cursor, license_number, address, city, region):
    """INSERT or UPDATE the single address row for a driver."""
    try:
        cursor.execute(
            "SELECT licenseNumber FROM driver_address WHERE licenseNumber = %s",
            (license_number,)
        )
        if cursor.fetchone():
            cursor.execute("""
                UPDATE driver_address
                   SET address = %s, city = %s, region = %s
                 WHERE licenseNumber = %s
            """, (address, city, region, license_number))
        else:
            cursor.execute("""
                INSERT INTO driver_address (licenseNumber, address, city, region)
                VALUES (%s, %s, %s, %s)
            """, (license_number, address, city, region))
        conn.commit()
        return True, "Address saved."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
