"""
db/reports.py
LTO IMS — 7 required report queries (uses SQL views defined in schema.sql).
"""


def report_all_drivers(conn, cursor, license_type=None, license_status=None,
                       age_min=None, age_max=None, sex=None):
    """
    Report 1 — All registered drivers, filterable.
    Uses allDrivers view (includes address JOIN).
    Rows: (licenseNumber, fullName, licenseStatus, licenseType,
           licenseIssuanceDate, licenseExpirationDate,
           dateOfBirth, age, sex, address, city, region)
    """
    query = "SELECT * FROM allDrivers WHERE 1=1"
    params = []

    if license_type:
        query += " AND licenseType = %s"
        params.append(license_type)
    if license_status:
        query += " AND licenseStatus = %s"
        params.append(license_status)
    if age_min is not None:
        query += " AND age >= %s"
        params.append(age_min)
    if age_max is not None:
        query += " AND age <= %s"
        params.append(age_max)
    if sex:
        query += " AND sex = %s"
        params.append(sex)

    query += " ORDER BY fullName"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def report_vehicles_by_driver(conn, cursor, license_number):
    """
    Report 2 — All vehicles owned by a given driver.
    Rows: (licenseNumber, fullName, plateNumber, make, model, type, color, year)
    """
    try:
        cursor.execute(
            "SELECT * FROM driverVehicles "
            "WHERE licenseNumber = %s ORDER BY plateNumber",
            (license_number,)
        )
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def report_expired_vehicles(conn, cursor, as_of_date=None):
    """
    Report 3 — Vehicles with expired registrations.
    Rows: (plateNumber, make, model, type, color, year,
           licenseNumber, registrationNumber, registrationDate, expirationDate)
    """
    try:
        if as_of_date:
            cursor.execute("""
                SELECT v.plateNumber, v.make, v.model, v.type, v.color, v.year,
                       v.licenseNumber, r.registrationNumber,
                       r.registrationDate, r.expirationDate
                FROM vehicle v
                JOIN registration r ON v.plateNumber = r.plateNumber
                WHERE r.expirationDate < %s
                ORDER BY r.expirationDate
            """, (as_of_date,))
        else:
            cursor.execute("""
                SELECT plateNumber, make, model, type, color, year,
                       licenseNumber, registrationNumber,
                       registrationDate, expirationDate
                FROM expiredVehicles
                ORDER BY expirationDate
            """)
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def report_inactive_drivers(conn, cursor):
    """
    Report 4 — Drivers with expired/suspended/revoked licences.
    Uses inactiveDrivers view (includes address JOIN).
    Rows: (licenseNumber, fullName, licenseStatus, licenseType,
           licenseIssuanceDate, licenseExpirationDate,
           dateOfBirth, age, sex, address, city, region)
    """
    try:
        cursor.execute("SELECT * FROM inactiveDrivers ORDER BY fullName")
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def report_violations_by_driver(conn, cursor, license_number,
                                date_from=None, date_to=None):
    """
    Report 5 — Violations by a specific driver within a date range.
    Uses driverViolations view.
    Rows: (violationId, licenseNumber, fullName, plateNumber, status,
           type, location, violationDate, fineAmount, apprehendingOfficer)
    """
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
    except Exception as e:
        return False, f"Database error: {e}"


def report_violation_summary(conn, cursor, year):
    """
    Report 6 — Total violations per type for a given year.
    Uses violationSummary view (violationYear column from schema.sql).
    Rows: (violationType, violationYear, totalViolations)
    """
    try:
        cursor.execute(
            "SELECT * FROM violationSummary "
            "WHERE violationYear = %s ORDER BY totalViolations DESC",
            (year,)
        )
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"


def report_vehicles_in_violations_by_location(conn, cursor,
                                              city=None, region=None):
    """
    Report 7 — Vehicles involved in violations within a city or region.
    Uses vehiclesWithViolations view.
    Rows: (plateNumber, make, model, type, color, year, fullName, city, region)
    """
    query = "SELECT * FROM vehiclesWithViolations WHERE 1=1"
    params = []

    if city:
        query += " AND city LIKE %s"
        params.append(f"%{city}%")
    if region:
        query += " AND region LIKE %s"
        params.append(f"%{region}%")
    query += " ORDER BY region, city, plateNumber"

    try:
        cursor.execute(query, tuple(params))
        return True, cursor.fetchall()
    except Exception as e:
        return False, f"Database error: {e}"
