# LTO Information Management System

**CMSC 127 — File Processing and Database Systems**
2nd Semester AY 2025–2026 | University of the Philippines Los Baños

A desktop application that simulates a simplified Land Transportation Office (LTO) records management system. It supports full CRUD operations for drivers, vehicles, registrations, and traffic violations, and generates seven SQL-based reports — all backed by a MariaDB/MySQL database.

---

## Project Structure

```
CMSC127-Project/
├── main.py                  # Entry point — run this
├── config.py                # DB credentials, color palette, fonts, constants
├── schema.sql               # Database schema (tables, views)
├── seed_data.sql            # Sample data for testing
│
├── db/                      # Database layer
│   ├── __init__.py          # Re-exports all db functions
│   ├── drivers.py           # Driver CRUD + address upsert
│   ├── vehicles.py          # Vehicle CRUD
│   ├── registrations.py     # Registration CRUD
│   ├── violations.py        # Violation CRUD
│   ├── reports.py           # 7 report queries
│   ├── helpers.py           # Shared utilities (age calc, date parse)
│   └── utils.py             # get_all_plates / get_all_licenses
│
└── ui/                      # Presentation layer
    ├── __init__.py
    ├── app.py               # LTOApp root window, sidebar, dashboard
    ├── widgets.py           # Reusable widget factory helpers
    ├── drivers_ui.py        # Driver screens
    ├── vehicles_ui.py       # Vehicle screens
    ├── registrations_ui.py  # Registration screens
    ├── violations_ui.py     # Violation screens
    └── reports_ui.py        # Report screens (R1 – R7)
```

---

## Features

### Driver Management
- Add, view/search, edit, and delete driver records
- Fields: license number, full name, date of birth, sex, license type, license status, issuance and expiration dates
- Optional address stored in a separate driver_address table (city, region)
- Filter by license type, status, sex, and age range

### Vehicle Management
- Register vehicles and associate them with a driver 
- Fields: plate number, engine number, chassis number, make, model, color, type, year
- Search by plate number, make, type, or owner license number

### Registration Management
- Record and track vehicle registrations and renewals
- Fields: registration number, plate number, registration date, expiration date, status
- Full registration history maintained per vehicle

### Traffic Violation Management
- Record violations linked to both a driver and a vehicle
- Fields: violation ID, type, location, date, fine amount, apprehending officer (optional), status
- Filter by license number, plate number, status, and date range

### Reports (SQL view-based)
| # | Report |
|---|--------|
| R1 | All registered drivers — filterable by type, status, age range, sex |
| R2 | All vehicles owned by a given driver |
| R3 | Vehicles with expired registrations as of a given date |
| R4 | Inactive drivers (expired, suspended, or revoked licenses) |
| R5 | Violations committed by a given driver within a date range |
| R6 | Total violation count per type for a given year |
| R7 | Vehicles involved in violations within a given city or region |

---

## 🛠 Requirements

### System
- Python **3.10** or higher
- **MariaDB 10.x / 11.x / 12.x** or MySQL 8.0+

### Python Packages

| Package | Purpose |
|---------|---------|
| `customtkinter` | Modern themed UI widgets built on top of Tkinter |
| `PyMySQL` | Pure-Python MySQL/MariaDB database connector |

Install all dependencies with:

```bash
pip install customtkinter PyMySQL
```

> **Note:** `tkinter` and `ttk` are part of Python's standard library — no separate install needed.

---

## Database Setup

### 1. Start MariaDB / MySQL

Make sure your database server is running. If `mysql` is not in your PATH, use the full path to the executable:

```powershell
# Example for MariaDB on Windows
& "C:\Program Files\MariaDB 12.2\bin\mysql.exe" -u root -p
```

### 2. Fix authentication (MariaDB 12.x only)

MariaDB 12.x uses `auth_gssapi_client` by default, which PyMySQL does not support. Run these commands inside the MariaDB shell to switch to native password auth:

```sql
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('your_password');
FLUSH PRIVILEGES;
EXIT;
```

### 3. Create the database and tables

```bash
mysql -u root -p < schema.sql
```

Or paste the contents of `schema.sql` directly into HeidiSQL / MySQL Workbench and execute it.

### 4. (Optional) Load sample data

```bash
mysql -u root -p ltodata < seed_data.sql
```

### 5. Update credentials in `config.py`

```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "your_password",   # ← change this
    "database": "ltodata",
    "port":     3306,
}
```

---

## Running the Application

From the project root directory:

```bash
python main.py
```

The application window will open. Use the sidebar on the left to navigate between modules.

---

## 🗄️ Database Schema Overview

```
driver              — core driver and license information
driver_address      — one address record per driver (city, region)
vehicle             — motor vehicle records linked to a driver
registration        — registration history per vehicle
violation           — traffic violation records
violation_date      — date dimension table (month, day, year) for violations
```

Seven SQL **views** are defined in schema.sql and used by the report screens:

```
allDrivers               — drivers with address join
driverVehicles           — vehicles per driver
expiredVehicles          — vehicles with expired registrations
inactiveDrivers          — expired / suspended / revoked drivers
driverViolations         — violations with driver name
violationSummary         — violation count per type per year
vehiclesWithViolations   — vehicles in violations with city/region
```