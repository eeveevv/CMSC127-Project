"""
db/registrations.py
LTO IMS — Registration CRUD operations.
"""


def add_registration_db(conn, cursor, reg_number, plate, status,
                        reg_date, exp_date):
    try:
        cursor.execute(
            "SELECT registrationNumber FROM registration "
            "WHERE registrationNumber = %s",
            (reg_number,)
        )
        if cursor.fetchone():
            return False, "Error: Registration number already exists."

        cursor.execute("""
            INSERT INTO registration
                (registrationNumber, plateNumber, status,
                 registrationDate, expirationDate)
            VALUES (%s, %s, %s, %s, %s)
        """, (reg_number, plate, status, reg_date, exp_date))
        conn.commit()
        return True, "Registration added successfully."
    except Exception as e:
        conn.rollback()
        if e.args[0] == 1452:
            return False, "Error: Plate number does not exist."
        return False, f"Database error: {e}"


def get_registrations_db(conn, cursor, plate=None):
    """
    Rows: (registrationNumber, plateNumber, status,
           registrationDate, expirationDate, make, model)
    """
    query = """
        SELECT r.registrationNumber, r.plateNumber, r.status,
               r.registrationDate, r.expirationDate,
               v.make, v.model
        FROM registration r
        JOIN vehicle v ON r.plateNumber = v.plateNumber
    """
    params = []
    if plate:
        query += " WHERE r.plateNumber = %s"
        params.append(plate)
    query += " ORDER BY r.expirationDate DESC"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def edit_registration_db(conn, cursor, reg_number, updates):
    try:
        cursor.execute(
            "SELECT registrationNumber FROM registration "
            "WHERE registrationNumber = %s",
            (reg_number,)
        )
        if not cursor.fetchone():
            return False, "Error: Registration not found."

        set_clause = ", ".join(f"{k} = %s" for k in updates)
        cursor.execute(
            f"UPDATE registration SET {set_clause} "
            f"WHERE registrationNumber = %s",
            list(updates.values()) + [reg_number]
        )
        conn.commit()
        return True, "Registration updated successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_registration_db(conn, cursor, reg_number):
    try:
        cursor.execute(
            "SELECT registrationNumber FROM registration "
            "WHERE registrationNumber = %s",
            (reg_number,)
        )
        if not cursor.fetchone():
            return False, "Error: Registration not found."

        cursor.execute(
            "DELETE FROM registration WHERE registrationNumber = %s",
            (reg_number,)
        )
        conn.commit()
        return True, "Registration deleted successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
