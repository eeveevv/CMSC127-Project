"""
db/vehicles.py
LTO IMS — Vehicle CRUD operations.
"""


def add_vehicle_db(conn, cursor, plate, engine, chassis, make, model,
                   color, vtype, year, license_number):
    try:
        cursor.execute(
            "SELECT plateNumber FROM vehicle WHERE plateNumber = %s", (plate,)
        )
        if cursor.fetchone():
            return False, "Error: Plate number already exists."

        cursor.execute("""
            INSERT INTO vehicle
                (plateNumber, engineNumber, chassisNumber, make, model,
                 color, type, year, licenseNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (plate, engine, chassis, make, model, color, vtype, year,
              license_number))
        conn.commit()
        return True, f"Vehicle '{plate}' added successfully."
    except Exception as e:
        conn.rollback()
        if e.args[0] == 1452:
            return False, "Error: License number does not exist."
        if e.args[0] == 1062:
            return False, "Error: Engine or chassis number already registered."
        return False, f"Database error: {e}"


def get_vehicles_db(conn, cursor, criteria=None):
    """
    Rows: (plateNumber, engineNumber, chassisNumber, make, model,
           color, type, year, licenseNumber, fullName)
    """
    query = """
        SELECT v.plateNumber, v.engineNumber, v.chassisNumber,
               v.make, v.model, v.color, v.type, v.year,
               v.licenseNumber, d.fullName
        FROM vehicle v
        JOIN driver d ON v.licenseNumber = d.licenseNumber
    """
    params, filters = [], []

    if criteria:
        if criteria.get("plateNumber"):
            filters.append("v.plateNumber LIKE %s")
            params.append(f"%{criteria['plateNumber']}%")
        if criteria.get("licenseNumber"):
            filters.append("v.licenseNumber = %s")
            params.append(criteria["licenseNumber"])
        if criteria.get("make"):
            filters.append("v.make LIKE %s")
            params.append(f"%{criteria['make']}%")
        if criteria.get("type"):
            filters.append("v.type = %s")
            params.append(criteria["type"])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY v.plateNumber"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def edit_vehicle_db(conn, cursor, plate, updates):
    try:
        cursor.execute(
            "SELECT plateNumber FROM vehicle WHERE plateNumber = %s", (plate,)
        )
        if not cursor.fetchone():
            return False, "Error: Vehicle not found."

        set_clause = ", ".join(f"{k} = %s" for k in updates)
        cursor.execute(
            f"UPDATE vehicle SET {set_clause} WHERE plateNumber = %s",
            list(updates.values()) + [plate]
        )
        conn.commit()
        return True, "Vehicle updated successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_vehicle_db(conn, cursor, plate):
    try:
        cursor.execute(
            "SELECT make, model FROM vehicle WHERE plateNumber = %s", (plate,)
        )
        row = cursor.fetchone()
        if not row:
            return False, "Error: Vehicle not found."

        cursor.execute(
            "DELETE FROM vehicle WHERE plateNumber = %s", (plate,)
        )
        conn.commit()
        return True, f"Vehicle '{row[0]} {row[1]}' deleted successfully."
    except Exception as e:
        conn.rollback()
        if e.args[0] == 1451:
            return False, "Cannot delete: vehicle has linked registrations or violations."
        return False, f"Database error: {e}"
