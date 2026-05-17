-- ============================================================
--  LTO Information Management System — Schema
--  CMSC 127 | 2nd Semester AY 2025–2026
--  Compatible with: MySQL / MariaDB
-- ============================================================

DROP DATABASE IF EXISTS ltodata;
CREATE DATABASE ltodata;
USE ltodata;

-- ============================================================
-- DRIVER
-- Removed redundant `address` column (handled by driver_address)
-- age is kept but should ideally be computed; retained per spec
-- ============================================================
CREATE TABLE driver (
    licenseNumber       BIGINT          NOT NULL,
    fullName            VARCHAR(60)     NOT NULL,
    licenseStatus       VARCHAR(10)     NOT NULL,   -- Valid, Expired, Suspended, Revoked
    licenseType         VARCHAR(20)     NOT NULL,   -- Student Permit, Non-Professional, Professional
    licenseIssuanceDate DATE            NOT NULL,
    licenseExpirationDate DATE          NOT NULL,
    dateOfBirth         DATE            NOT NULL,
    age                 TINYINT UNSIGNED NOT NULL,
    sex                 VARCHAR(6)      NOT NULL,   -- Male, Female
    CONSTRAINT driver_licenseNumber_pk      PRIMARY KEY (licenseNumber),
    CONSTRAINT driver_licenseStatus_chk    CHECK (licenseStatus IN ('Valid', 'Expired', 'Suspended', 'Revoked')),
    CONSTRAINT driver_licenseType_chk      CHECK (licenseType   IN ('Student Permit', 'Non-Professional', 'Professional')),
    CONSTRAINT driver_sex_chk              CHECK (sex           IN ('Male', 'Female'))
);

-- ============================================================
-- DRIVER_ADDRESS
-- Added licenseNumber as PK (one address per driver).
-- Extend to a composite PK or surrogate key if multi-address is needed.
-- ============================================================
CREATE TABLE driver_address (
    licenseNumber   BIGINT          NOT NULL,
    address         VARCHAR(100)    NOT NULL,
    city            VARCHAR(50)     NOT NULL,
    region          VARCHAR(50)     NOT NULL,
    CONSTRAINT driver_address_pk                PRIMARY KEY (licenseNumber),
    CONSTRAINT driver_address_licenseNumber_fk  FOREIGN KEY (licenseNumber) REFERENCES driver(licenseNumber)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================
-- VEHICLE
-- Each vehicle is associated with exactly one registered owner (driver).
-- ============================================================
CREATE TABLE vehicle (
    plateNumber     VARCHAR(15)     NOT NULL,
    engineNumber    VARCHAR(17)     NOT NULL,
    chassisNumber   VARCHAR(17)     NOT NULL,
    make            VARCHAR(30)     NOT NULL,
    model           VARCHAR(30)     NOT NULL,
    color           VARCHAR(15)     NOT NULL,
    type            VARCHAR(30)     NOT NULL,   -- Motorcycle, Private Car, Public Utility Vehicle, etc.
    year            YEAR            NOT NULL,
    licenseNumber   BIGINT          NOT NULL,
    CONSTRAINT vehicle_plateNumber_pk       PRIMARY KEY (plateNumber),
    CONSTRAINT vehicle_engineNumber_uk      UNIQUE (engineNumber),
    CONSTRAINT vehicle_chassisNumber_uk     UNIQUE (chassisNumber),
    CONSTRAINT vehicle_licenseNumber_fk     FOREIGN KEY (licenseNumber) REFERENCES driver(licenseNumber)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================================
-- REGISTRATION
-- Tracks full registration history per vehicle (multiple rows allowed).
-- ============================================================
CREATE TABLE registration (
    registrationNumber  VARCHAR(15)     NOT NULL,
    plateNumber         VARCHAR(15)     NOT NULL,
    status              VARCHAR(10)     NOT NULL,   -- Active, Expired, Suspended
    registrationDate    DATE            NOT NULL,
    expirationDate      DATE            NOT NULL,
    CONSTRAINT registration_registrationNumber_pk   PRIMARY KEY (registrationNumber),
    CONSTRAINT registration_plateNumber_fk          FOREIGN KEY (plateNumber) REFERENCES vehicle(plateNumber)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT registration_status_chk             CHECK (status IN ('Active', 'Expired', 'Suspended'))
);

-- ============================================================
-- VIOLATION
-- Records traffic violations linked to both a driver and a vehicle.
-- ============================================================
CREATE TABLE violation (
    violationId             VARCHAR(15)     NOT NULL,
    licenseNumber           BIGINT          NOT NULL,
    plateNumber             VARCHAR(15)     NOT NULL,
    status                  VARCHAR(10)     NOT NULL,   -- Unpaid, Paid, Contested
    type                    VARCHAR(50)     NOT NULL,
    location                VARCHAR(100)    NOT NULL,
    violationDate           DATE            NOT NULL,
    fineAmount              DECIMAL(10, 2)  NOT NULL,
    apprehendingOfficer     VARCHAR(60)     NULL,       -- optional per spec
    CONSTRAINT violation_violationId_pk         PRIMARY KEY (violationId),
    CONSTRAINT violation_licenseNumber_fk       FOREIGN KEY (licenseNumber) REFERENCES driver(licenseNumber)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT violation_plateNumber_fk         FOREIGN KEY (plateNumber)   REFERENCES vehicle(plateNumber)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT violation_status_chk             CHECK (status IN ('Unpaid', 'Paid', 'Contested'))
);

-- ============================================================
-- VIOLATION_DATE
-- Date dimension table. violationId is the PK (1-to-1 with violation).
-- ============================================================
CREATE TABLE violation_date (
    violationId     VARCHAR(15)     NOT NULL,
    violationDate   DATE            NOT NULL,
    month           TINYINT         NOT NULL,
    day             TINYINT         NOT NULL,
    year            YEAR            NOT NULL,
    CONSTRAINT violation_date_pk            PRIMARY KEY (violationId),
    CONSTRAINT violation_date_violationId_fk FOREIGN KEY (violationId) REFERENCES violation(violationId)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================
-- VIEWS
-- ============================================================

-- 1. All registered drivers (base view; filter at app/query layer)
CREATE VIEW allDrivers AS
SELECT
    d.licenseNumber,
    d.fullName,
    d.licenseStatus,
    d.licenseType,
    d.licenseIssuanceDate,
    d.licenseExpirationDate,
    d.dateOfBirth,
    d.age,
    d.sex,
    da.address,
    da.city,
    da.region
FROM driver d
LEFT JOIN driver_address da ON d.licenseNumber = da.licenseNumber;

-- 2. All vehicles owned by each driver
CREATE VIEW driverVehicles AS
SELECT
    d.licenseNumber,
    d.fullName,
    v.plateNumber,
    v.make,
    v.model,
    v.type,
    v.color,
    v.year
FROM driver d
JOIN vehicle v ON d.licenseNumber = v.licenseNumber;

-- 3. Vehicles with expired registrations (as of current date)
CREATE VIEW expiredVehicles AS
SELECT
    v.*,
    r.registrationNumber,
    r.registrationDate,
    r.expirationDate
FROM vehicle v
JOIN registration r ON v.plateNumber = r.plateNumber
WHERE r.status = 'Expired'
   OR r.expirationDate < CURDATE();

-- 4. Drivers with expired or suspended licenses
CREATE VIEW inactiveDrivers AS
SELECT
    d.*,
    da.address,
    da.city,
    da.region
FROM driver d
LEFT JOIN driver_address da ON d.licenseNumber = da.licenseNumber
WHERE d.licenseStatus IN ('Expired', 'Suspended', 'Revoked')
   OR d.licenseExpirationDate < CURDATE();

-- 5. All violations with driver and vehicle info (filter by driver/date at query layer)
CREATE VIEW driverViolations AS
SELECT
    vi.violationId,
    vi.licenseNumber,
    d.fullName,
    vi.plateNumber,
    vi.status,
    vi.type,
    vi.location,
    vi.violationDate,
    vi.fineAmount,
    vi.apprehendingOfficer
FROM violation vi
JOIN driver d ON vi.licenseNumber = d.licenseNumber;

-- 6. Total violations per type AND per year (FIXED: year now included in SELECT)
CREATE VIEW violationSummary AS
SELECT
    type                        AS violationType,
    YEAR(violationDate)         AS violationYear,
    COUNT(*)                    AS totalViolations
FROM violation
GROUP BY type, YEAR(violationDate)
ORDER BY violationYear, totalViolations DESC;

-- 7. Vehicles involved in violations, with city/region (filter at query layer)
CREATE VIEW vehiclesWithViolations AS
SELECT DISTINCT
    v.plateNumber,
    v.make,
    v.model,
    v.type,
    v.color,
    v.year,
    d.fullName,
    da.city,
    da.region
FROM vehicle v
JOIN violation  vi ON v.plateNumber   = vi.plateNumber
JOIN driver     d  ON v.licenseNumber = d.licenseNumber
JOIN driver_address da ON d.licenseNumber = da.licenseNumber;

-- ============================================================
-- SAMPLE REPORT QUERIES (uncomment to run)
-- ============================================================

-- View all drivers
-- SELECT * FROM allDrivers;

-- Filter by license type
-- SELECT * FROM allDrivers WHERE licenseType = 'Professional';

-- Filter by license status
-- SELECT * FROM allDrivers WHERE licenseStatus = 'Valid';

-- Filter by age range
-- SELECT * FROM allDrivers WHERE age BETWEEN 25 AND 40;

-- Filter by sex
-- SELECT * FROM allDrivers WHERE sex = 'Female';

-- All vehicles owned by a specific driver
-- SELECT * FROM driverVehicles WHERE licenseNumber = 1000001;

-- Vehicles with expired registrations as of a given date
-- SELECT * FROM expiredVehicles WHERE expirationDate < '2025-01-01';

-- Drivers with expired or suspended licenses
-- SELECT * FROM inactiveDrivers;

-- Violations by a specific driver within a date range
-- SELECT * FROM driverViolations
-- WHERE licenseNumber = 1000001
--   AND violationDate BETWEEN '2024-01-01' AND '2024-12-31';

-- Total violations per type for a given year
-- SELECT * FROM violationSummary WHERE violationYear = 2024;

-- Vehicles involved in violations in a given city
-- SELECT * FROM vehiclesWithViolations WHERE city = 'Cebu City';

-- Vehicles involved in violations in a given region
-- SELECT * FROM vehiclesWithViolations WHERE region = 'NCR';