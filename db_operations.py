"""
db_operations.py
LTO Information Management System — Database Operations
CMSC 127 | 2nd Semester AY 2025-2026
"""

import datetime
from mysql.connector import Error


# ─────────────────────────────────────────────
# DRIVER CRUD
# ─────────────────────────────────────────────

def add_driver_db(conn, cursor, license_number, full_name, license_status,
                  license_type, issuance_date, expiration_date, dob, sex):
    try:
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        today = datetime.date.today()
        age = today.year - dob_date.year
        if (today.month, today.day) < (dob_date.month, dob_date.day):
            age -= 1

        cursor.execute("SELECT licenseNumber FROM driver WHERE licenseNumber = %s", (license_number,))
        if cursor.fetchone():
            return False, "Error: License number already exists."

        cursor.execute("""
            INSERT INTO driver
            (licenseNumber, fullName, licenseStatus, licenseType,
             licenseIssuanceDate, licenseExpirationDate, dateOfBirth, age, sex)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (license_number, full_name, license_status, license_type,
              issuance_date, expiration_date, dob, age, sex))
        conn.commit()
        return True, "Driver added successfully."
    except ValueError:
        conn.rollback()
        return False, "Error: Invalid date format. Use YYYY-MM-DD."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


def get_drivers_db(conn, cursor, criteria=None):
    query = """
        SELECT d.licenseNumber, d.fullName, d.licenseStatus, d.licenseType,
               d.licenseIssuanceDate, d.licenseExpirationDate,
               d.dateOfBirth, d.age, d.sex,
               da.address, da.city, da.region
        FROM driver d
        LEFT JOIN driver_address da ON d.licenseNumber = da.licenseNumber
    """
    params = []
    filters = []

    if criteria:
        if criteria.get('licenseNumber'):
            filters.append("d.licenseNumber = %s")
            params.append(criteria['licenseNumber'])
        if criteria.get('fullName'):
            filters.append("d.fullName LIKE %s")
            params.append(f"%{criteria['fullName']}%")
        if criteria.get('licenseType'):
            filters.append("d.licenseType = %s")
            params.append(criteria['licenseType'])
        if criteria.get('licenseStatus'):
            filters.append("d.licenseStatus = %s")
            params.append(criteria['licenseStatus'])
        if criteria.get('sex'):
            filters.append("d.sex = %s")
            params.append(criteria['sex'])
        if criteria.get('age_min'):
            filters.append("d.age >= %s")
            params.append(criteria['age_min'])
        if criteria.get('age_max'):
            filters.append("d.age <= %s")
            params.append(criteria['age_max'])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY d.fullName"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def edit_driver_db(conn, cursor, license_number, updates):
    try:
        cursor.execute("SELECT licenseNumber FROM driver WHERE licenseNumber = %s", (license_number,))
        if not cursor.fetchone():
            return False, "Error: Driver not found."

        db_updates = {}
        for k, v in updates.items():
            if k == 'dateOfBirth':
                dob = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                today = datetime.date.today()
                age = today.year - dob.year
                if (today.month, today.day) < (dob.month, dob.day):
                    age -= 1
                db_updates['dateOfBirth'] = v
                db_updates['age'] = age
            else:
                db_updates[k] = v

        if not db_updates:
            return False, "No changes provided."

        set_clause = ", ".join([f"{k} = %s" for k in db_updates])
        cursor.execute(
            f"UPDATE driver SET {set_clause} WHERE licenseNumber = %s",
            list(db_updates.values()) + [license_number]
        )
        conn.commit()
        return True, "Driver updated successfully."
    except ValueError:
        conn.rollback()
        return False, "Error: Invalid date format."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_driver_db(conn, cursor, license_number):
    try:
        cursor.execute("SELECT fullName FROM driver WHERE licenseNumber = %s", (license_number,))
        row = cursor.fetchone()
        if not row:
            return False, "Error: Driver not found."
        cursor.execute("DELETE FROM driver WHERE licenseNumber = %s", (license_number,))
        conn.commit()
        return True, f"Driver '{row[0]}' deleted successfully."
    except Error as e:
        conn.rollback()
        if e.errno == 1451:
            return False, "Cannot delete: driver has associated vehicles or violations."
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# DRIVER ADDRESS
# ─────────────────────────────────────────────

def upsert_driver_address_db(conn, cursor, license_number, address, city, region):
    try:
        cursor.execute("SELECT licenseNumber FROM driver_address WHERE licenseNumber = %s", (license_number,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE driver_address SET address=%s, city=%s, region=%s
                WHERE licenseNumber=%s
            """, (address, city, region, license_number))
        else:
            cursor.execute("""
                INSERT INTO driver_address (licenseNumber, address, city, region)
                VALUES (%s, %s, %s, %s)
            """, (license_number, address, city, region))
        conn.commit()
        return True, "Address saved."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# VEHICLE CRUD
# ─────────────────────────────────────────────

def add_vehicle_db(conn, cursor, plate, engine, chassis, make, model,
                   color, vtype, year, license_number):
    try:
        cursor.execute("SELECT plateNumber FROM vehicle WHERE plateNumber = %s", (plate,))
        if cursor.fetchone():
            return False, "Error: Plate number already exists."
        cursor.execute("""
            INSERT INTO vehicle
            (plateNumber, engineNumber, chassisNumber, make, model,
             color, type, year, licenseNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (plate, engine, chassis, make, model, color, vtype, year, license_number))
        conn.commit()
        return True, "Vehicle added successfully."
    except Error as e:
        conn.rollback()
        if e.errno == 1452:
            return False, "Error: License number does not exist."
        if e.errno == 1062:
            return False, "Error: Engine or chassis number already exists."
        return False, f"Database error: {e}"


def get_vehicles_db(conn, cursor, criteria=None):
    query = """
        SELECT v.plateNumber, v.engineNumber, v.chassisNumber,
               v.make, v.model, v.color, v.type, v.year,
               v.licenseNumber, d.fullName
        FROM vehicle v
        JOIN driver d ON v.licenseNumber = d.licenseNumber
    """
    params = []
    filters = []

    if criteria:
        if criteria.get('plateNumber'):
            filters.append("v.plateNumber LIKE %s")
            params.append(f"%{criteria['plateNumber']}%")
        if criteria.get('licenseNumber'):
            filters.append("v.licenseNumber = %s")
            params.append(criteria['licenseNumber'])
        if criteria.get('make'):
            filters.append("v.make LIKE %s")
            params.append(f"%{criteria['make']}%")
        if criteria.get('type'):
            filters.append("v.type = %s")
            params.append(criteria['type'])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY v.plateNumber"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def edit_vehicle_db(conn, cursor, plate, updates):
    try:
        cursor.execute("SELECT plateNumber FROM vehicle WHERE plateNumber = %s", (plate,))
        if not cursor.fetchone():
            return False, "Error: Vehicle not found."
        set_clause = ", ".join([f"{k} = %s" for k in updates])
        cursor.execute(
            f"UPDATE vehicle SET {set_clause} WHERE plateNumber = %s",
            list(updates.values()) + [plate]
        )
        conn.commit()
        return True, "Vehicle updated successfully."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_vehicle_db(conn, cursor, plate):
    try:
        cursor.execute("SELECT make, model FROM vehicle WHERE plateNumber = %s", (plate,))
        row = cursor.fetchone()
        if not row:
            return False, "Error: Vehicle not found."
        cursor.execute("DELETE FROM vehicle WHERE plateNumber = %s", (plate,))
        conn.commit()
        return True, f"Vehicle '{row[0]} {row[1]}' deleted successfully."
    except Error as e:
        conn.rollback()
        if e.errno == 1451:
            return False, "Cannot delete: vehicle has associated registrations or violations."
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# REGISTRATION CRUD
# ─────────────────────────────────────────────

def add_registration_db(conn, cursor, reg_number, plate, status, reg_date, exp_date):
    try:
        cursor.execute("SELECT registrationNumber FROM registration WHERE registrationNumber = %s", (reg_number,))
        if cursor.fetchone():
            return False, "Error: Registration number already exists."
        cursor.execute("""
            INSERT INTO registration
            (registrationNumber, plateNumber, status, registrationDate, expirationDate)
            VALUES (%s, %s, %s, %s, %s)
        """, (reg_number, plate, status, reg_date, exp_date))
        conn.commit()
        return True, "Registration added successfully."
    except Error as e:
        conn.rollback()
        if e.errno == 1452:
            return False, "Error: Plate number does not exist."
        return False, f"Database error: {e}"


def get_registrations_db(conn, cursor, plate=None):
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
    except Error as e:
        return False, f"Database error: {e}"


def edit_registration_db(conn, cursor, reg_number, updates):
    try:
        cursor.execute("SELECT registrationNumber FROM registration WHERE registrationNumber = %s", (reg_number,))
        if not cursor.fetchone():
            return False, "Error: Registration not found."
        set_clause = ", ".join([f"{k} = %s" for k in updates])
        cursor.execute(
            f"UPDATE registration SET {set_clause} WHERE registrationNumber = %s",
            list(updates.values()) + [reg_number]
        )
        conn.commit()
        return True, "Registration updated successfully."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_registration_db(conn, cursor, reg_number):
    try:
        cursor.execute("SELECT registrationNumber FROM registration WHERE registrationNumber = %s", (reg_number,))
        if not cursor.fetchone():
            return False, "Error: Registration not found."
        cursor.execute("DELETE FROM registration WHERE registrationNumber = %s", (reg_number,))
        conn.commit()
        return True, "Registration deleted successfully."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# VIOLATION CRUD
# ─────────────────────────────────────────────

def add_violation_db(conn, cursor, vio_id, license_number, plate,
                     status, vtype, location, vio_date, fine, officer):
    try:
        cursor.execute("SELECT violationId FROM violation WHERE violationId = %s", (vio_id,))
        if cursor.fetchone():
            return False, "Error: Violation ID already exists."

        cursor.execute("""
            INSERT INTO violation
            (violationId, licenseNumber, plateNumber, status, type,
             location, violationDate, fineAmount, apprehendingOfficer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (vio_id, license_number, plate, status, vtype,
              location, vio_date, fine, officer if officer else None))

        # Auto-populate violation_date
        d = datetime.datetime.strptime(vio_date, '%Y-%m-%d').date()
        cursor.execute("""
            INSERT INTO violation_date (violationId, violationDate, month, day, year)
            VALUES (%s, %s, %s, %s, %s)
        """, (vio_id, vio_date, d.month, d.day, d.year))

        conn.commit()
        return True, "Violation recorded successfully."
    except Error as e:
        conn.rollback()
        if e.errno == 1452:
            return False, "Error: License number or plate number does not exist."
        return False, f"Database error: {e}"


def get_violations_db(conn, cursor, criteria=None):
    query = """
        SELECT vi.violationId, vi.licenseNumber, d.fullName,
               vi.plateNumber, vi.status, vi.type,
               vi.location, vi.violationDate, vi.fineAmount,
               vi.apprehendingOfficer
        FROM violation vi
        JOIN driver d ON vi.licenseNumber = d.licenseNumber
    """
    params = []
    filters = []

    if criteria:
        if criteria.get('licenseNumber'):
            filters.append("vi.licenseNumber = %s")
            params.append(criteria['licenseNumber'])
        if criteria.get('plateNumber'):
            filters.append("vi.plateNumber LIKE %s")
            params.append(f"%{criteria['plateNumber']}%")
        if criteria.get('status'):
            filters.append("vi.status = %s")
            params.append(criteria['status'])
        if criteria.get('date_from'):
            filters.append("vi.violationDate >= %s")
            params.append(criteria['date_from'])
        if criteria.get('date_to'):
            filters.append("vi.violationDate <= %s")
            params.append(criteria['date_to'])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY vi.violationDate DESC"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def edit_violation_db(conn, cursor, vio_id, updates):
    try:
        cursor.execute("SELECT violationId FROM violation WHERE violationId = %s", (vio_id,))
        if not cursor.fetchone():
            return False, "Error: Violation not found."
        set_clause = ", ".join([f"{k} = %s" for k in updates])
        cursor.execute(
            f"UPDATE violation SET {set_clause} WHERE violationId = %s",
            list(updates.values()) + [vio_id]
        )
        conn.commit()
        return True, "Violation updated successfully."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


def delete_violation_db(conn, cursor, vio_id):
    try:
        cursor.execute("SELECT violationId FROM violation WHERE violationId = %s", (vio_id,))
        if not cursor.fetchone():
            return False, "Error: Violation not found."
        cursor.execute("DELETE FROM violation WHERE violationId = %s", (vio_id,))
        conn.commit()
        return True, "Violation deleted successfully."
    except Error as e:
        conn.rollback()
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# REPORTS  (all 7 from project specs)
# ─────────────────────────────────────────────

def report_all_drivers(conn, cursor, license_type=None, license_status=None,
                       age_min=None, age_max=None, sex=None):
    """Report 1 — All registered drivers with optional filters."""
    query = "SELECT * FROM allDrivers WHERE 1=1"
    params = []
    if license_type:
        query += " AND licenseType = %s"
        params.append(license_type)
    if license_status:
        query += " AND licenseStatus = %s"
        params.append(license_status)
    if age_min:
        query += " AND age >= %s"
        params.append(age_min)
    if age_max:
        query += " AND age <= %s"
        params.append(age_max)
    if sex:
        query += " AND sex = %s"
        params.append(sex)
    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def report_vehicles_by_driver(conn, cursor, license_number):
    """Report 2 — All vehicles owned by a given driver."""
    try:
        cursor.execute("SELECT * FROM driverVehicles WHERE licenseNumber = %s", (license_number,))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def report_expired_vehicles(conn, cursor, as_of_date=None):
    """Report 3 — Vehicles with expired registrations as of a given date."""
    try:
        if as_of_date:
            cursor.execute("""
                SELECT v.plateNumber, v.make, v.model, v.type, v.color, v.year,
                       v.licenseNumber, r.registrationNumber, r.registrationDate, r.expirationDate
                FROM vehicle v
                JOIN registration r ON v.plateNumber = r.plateNumber
                WHERE r.expirationDate < %s
                ORDER BY r.expirationDate
            """, (as_of_date,))
        else:
            cursor.execute("SELECT * FROM expiredVehicles ORDER BY expirationDate")
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def report_inactive_drivers(conn, cursor):
    """Report 4 — Drivers with expired or suspended licenses."""
    try:
        cursor.execute("SELECT * FROM inactiveDrivers ORDER BY fullName")
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def report_violations_by_driver(conn, cursor, license_number, date_from=None, date_to=None):
    """Report 5 — Violations by a driver within a date range."""
    query = "SELECT * FROM driverViolations WHERE licenseNumber = %s"
    params = [license_number]
    if date_from:
        query += " AND violationDate >= %s"
        params.append(date_from)
    if date_to:
        query += " AND violationDate <= %s"
        params.append(date_to)
    query += " ORDER BY violationDate DESC"
    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def report_violation_summary(conn, cursor, year):
    """Report 6 — Total violations per type for a given year."""
    try:
        cursor.execute("SELECT * FROM violationSummary WHERE violationYear = %s", (year,))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


def report_vehicles_in_violations_by_location(conn, cursor, city=None, region=None):
    """Report 7 — Vehicles involved in violations by city or region."""
    query = "SELECT * FROM vehiclesWithViolations WHERE 1=1"
    params = []
    if city:
        query += " AND city = %s"
        params.append(city)
    if region:
        query += " AND region = %s"
        params.append(region)
    query += " ORDER BY region, city"
    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Error as e:
        return False, f"Database error: {e}"


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_all_plate_numbers(conn, cursor):
    try:
        cursor.execute("SELECT plateNumber FROM vehicle ORDER BY plateNumber")
        return [row[0] for row in cursor.fetchall()]
    except Error:
        return []


def get_all_license_numbers(conn, cursor):
    try:
        cursor.execute("SELECT licenseNumber, fullName FROM driver ORDER BY fullName")
        return cursor.fetchall()
    except Error:
        return []