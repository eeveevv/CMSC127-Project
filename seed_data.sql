-- ============================================================
--  LTO Information Management System — Seed Data
--  CMSC 127 | 2nd Semester AY 2025–2026
--  Run AFTER ltodata_schema.sql
-- ============================================================

USE ltodata;

-- ============================================================
-- 1. DRIVER  (no `address` column — lives in driver_address)
-- ============================================================
INSERT INTO driver (licenseNumber, fullName, licenseStatus, licenseType, licenseIssuanceDate, licenseExpirationDate, dateOfBirth, age, sex) VALUES
(1000001, 'Juan dela Cruz',     'Valid',     'Professional',     '2022-03-10', '2027-03-10', '1985-06-15', 39, 'Male'),
(1000002, 'Maria Santos',       'Valid',     'Non-Professional', '2023-07-21', '2028-07-21', '1992-11-03', 32, 'Female'),
(1000003, 'Roberto Reyes',      'Expired',   'Professional',     '2019-05-14', '2024-05-14', '1978-02-20', 46, 'Male'),
(1000004, 'Ana Gonzales',       'Valid',     'Non-Professional', '2024-01-08', '2029-01-08', '1999-08-30', 25, 'Female'),
(1000005, 'Carlos Mendoza',     'Suspended', 'Professional',     '2021-09-17', '2026-09-17', '1980-04-12', 44, 'Male'),
(1000006, 'Lourdes Bautista',   'Valid',     'Student Permit',   '2025-02-05', '2026-02-05', '2004-01-22', 21, 'Female'),
(1000007, 'Eduardo Villanueva', 'Valid',     'Professional',     '2023-11-30', '2028-11-30', '1975-07-09', 49, 'Male'),
(1000008, 'Jasmine Abad',       'Expired',   'Non-Professional', '2018-06-25', '2023-06-25', '1990-03-17', 34, 'Female'),
(1000009, 'Felix Domingo',      'Valid',     'Professional',     '2024-08-19', '2029-08-19', '1983-12-05', 41, 'Male'),
(1000010, 'Rosario Navarro',    'Valid',     'Non-Professional', '2022-10-11', '2027-10-11', '1995-05-28', 29, 'Female');

-- ============================================================
-- 2. DRIVER_ADDRESS
-- ============================================================
INSERT INTO driver_address (licenseNumber, address, city, region) VALUES
(1000001, 'Brgy. Mabini, Lipa City',        'Lipa City',       'CALABARZON'),
(1000002, 'Brgy. Halang, Calamba City',     'Calamba City',    'CALABARZON'),
(1000003, 'Brgy. Poblacion, Batangas City', 'Batangas City',   'CALABARZON'),
(1000004, 'Brgy. San Isidro, Taguig City',  'Taguig City',     'NCR'),
(1000005, 'Brgy. Bagong Ilog, Pasig City',  'Pasig City',      'NCR'),
(1000006, 'Brgy. Dolores, San Fernando',    'San Fernando',    'Central Luzon'),
(1000007, 'Brgy. San Vicente, Iloilo City', 'Iloilo City',     'Western Visayas'),
(1000008, 'Brgy. Tejeros, Makati City',     'Makati City',     'NCR'),
(1000009, 'Brgy. Parian, Cebu City',        'Cebu City',       'Central Visayas'),
(1000010, 'Brgy. Ugong, Valenzuela City',   'Valenzuela City', 'NCR');

-- ============================================================
-- 3. VEHICLE
-- ============================================================
INSERT INTO vehicle (plateNumber, engineNumber, chassisNumber, make, model, color, type, year, licenseNumber) VALUES
('AAA-1234', 'ENG001ABC123456', 'CHS001XYZ789012', 'Toyota',    'Vios',        'White',  'Private Car',           2020, 1000001),
('BBB-5678', 'ENG002DEF234567', 'CHS002UVW890123', 'Honda',     'Beat',        'Red',    'Motorcycle',            2021, 1000001),
('CCC-9012', 'ENG003GHI345678', 'CHS003RST901234', 'Mitsubishi','Montero',     'Black',  'Private Car',           2019, 1000002),
('DDD-3456', 'ENG004JKL456789', 'CHS004OPQ012345', 'Suzuki',    'Raider R150', 'Blue',   'Motorcycle',            2022, 1000003),
('EEE-7890', 'ENG005MNO567890', 'CHS005LMN123456', 'Ford',      'Ranger',      'Gray',   'Private Car',           2018, 1000004),
('FFF-2345', 'ENG006PQR678901', 'CHS006IJK234567', 'Toyota',    'Hiace',       'Yellow', 'Public Utility Vehicle',2017, 1000005),
('GGG-6789', 'ENG007STU789012', 'CHS007FGH345678', 'Honda',     'CR-V',        'Silver', 'Private Car',           2023, 1000006),
('HHH-0123', 'ENG008VWX890123', 'CHS008CDE456789', 'Yamaha',    'Mio',         'Pink',   'Motorcycle',            2020, 1000007),
('III-4567', 'ENG009YZA901234', 'CHS009ABB567890', 'Hyundai',   'Tucson',      'White',  'Private Car',           2021, 1000008),
('JJJ-8901', 'ENG010BCD012345', 'CHS010ZAA678901', 'Kia',       'Sportage',    'Green',  'Private Car',           2022, 1000009),
('KKK-2222', 'ENG011EFG123456', 'CHS011YBB789012', 'Isuzu',     'Elf',         'White',  'Public Utility Vehicle',2016, 1000010),
('LLL-3333', 'ENG012HIJ234567', 'CHS012XCC890123', 'Nissan',    'Navara',      'Brown',  'Private Car',           2020, 1000002);

-- ============================================================
-- 4. REGISTRATION
-- ============================================================
INSERT INTO registration (registrationNumber, plateNumber, status, registrationDate, expirationDate) VALUES
('REG-000001', 'AAA-1234', 'Active',    '2024-01-15', '2026-01-15'),
('REG-000002', 'BBB-5678', 'Active',    '2024-03-10', '2026-03-10'),
('REG-000003', 'CCC-9012', 'Expired',   '2022-06-20', '2024-06-20'),
('REG-000004', 'DDD-3456', 'Active',    '2025-02-01', '2027-02-01'),
('REG-000005', 'EEE-7890', 'Expired',   '2021-11-05', '2023-11-05'),
('REG-000006', 'FFF-2345', 'Suspended', '2023-04-18', '2025-04-18'),
('REG-000007', 'GGG-6789', 'Active',    '2025-05-22', '2027-05-22'),
('REG-000008', 'HHH-0123', 'Active',    '2024-09-30', '2026-09-30'),
('REG-000009', 'III-4567', 'Expired',   '2020-08-14', '2022-08-14'),
('REG-000010', 'JJJ-8901', 'Active',    '2025-01-07', '2027-01-07'),
('REG-000011', 'KKK-2222', 'Expired',   '2021-07-25', '2023-07-25'),
('REG-000012', 'LLL-3333', 'Active',    '2024-12-01', '2026-12-01'),
('REG-000013', 'AAA-1234', 'Expired',   '2022-01-15', '2024-01-15'),
('REG-000014', 'CCC-9012', 'Expired',   '2020-06-20', '2022-06-20');

-- ============================================================
-- 5. VIOLATION
-- Note: VIO-000014 corrected from invalid 2024-02-29 to 2024-02-28
-- ============================================================
INSERT INTO violation (violationId, licenseNumber, plateNumber, status, type, location, violationDate, fineAmount, apprehendingOfficer) VALUES
('VIO-000001', 1000001, 'AAA-1234', 'Unpaid',    'Overspeeding',              'EDSA Quezon City',               '2024-03-15', 2000.00, 'PO1 Ricardo Santos'),
('VIO-000002', 1000001, 'BBB-5678', 'Paid',      'No Helmet',                 'Diversion Road, Lipa City',      '2024-06-22', 1500.00, 'PO2 Manny Cruz'),
('VIO-000003', 1000002, 'CCC-9012', 'Unpaid',    'Reckless Driving',          'South Luzon Expressway',         '2023-11-08', 5000.00, 'PO1 Jerome Reyes'),
('VIO-000004', 1000003, 'DDD-3456', 'Contested', 'Illegal Parking',           'Brgy. Poblacion, Batangas City', '2024-01-30',  500.00, 'PO3 Allan Flores'),
('VIO-000005', 1000005, 'FFF-2345', 'Paid',      'Disregarding Traffic Sign', 'EDSA Mandaluyong',               '2023-07-19', 1000.00, 'PO1 Ben Castillo'),
('VIO-000006', 1000005, 'FFF-2345', 'Unpaid',    'Overspeeding',              'C5 Road, Taguig City',           '2024-05-03', 2000.00, 'PO2 Dante Villanueva'),
('VIO-000007', 1000007, 'HHH-0123', 'Paid',      'No Helmet',                 'Iloilo Diversion Road',          '2023-09-14', 1500.00, 'PO1 Grace Tan'),
('VIO-000008', 1000009, 'JJJ-8901', 'Unpaid',    'Reckless Driving',          'Osmena Blvd, Cebu City',         '2024-08-27', 5000.00, 'PO3 Ramon Uy'),
('VIO-000009', 1000010, 'KKK-2222', 'Paid',      'Illegal Parking',           'Session Road, Baguio City',      '2022-12-05',  500.00, 'PO2 Lisa Natividad'),
('VIO-000010', 1000004, 'EEE-7890', 'Unpaid',    'Overspeeding',              'Skyway, Paranaque City',         '2024-09-10', 2000.00, 'PO1 Mark Dela Rosa'),
('VIO-000011', 1000001, 'AAA-1234', 'Paid',      'Illegal Parking',           'Ayala Ave, Makati City',         '2023-04-18',  500.00, 'PO2 Joy Mercado'),
('VIO-000012', 1000002, 'LLL-3333', 'Contested', 'Reckless Driving',          'SLEX, Calamba City',             '2024-11-20', 5000.00, 'PO3 Ryan Buenaventura'),
('VIO-000013', 1000003, 'DDD-3456', 'Unpaid',    'Disregarding Traffic Sign', 'P. Burgos St, Batangas City',    '2023-02-14', 1000.00, 'PO1 Dennis Soriano'),
('VIO-000014', 1000007, 'HHH-0123', 'Paid',      'Overspeeding',              'Iloilo Circumferential Road',    '2024-02-28', 2000.00, 'PO2 Nina Espino'),
('VIO-000015', 1000009, 'JJJ-8901', 'Unpaid',    'No Helmet',                 'Colon St, Cebu City',            '2023-10-11', 1500.00, 'PO1 Vincent Lim');

-- ============================================================
-- 6. VIOLATION_DATE
-- ============================================================
INSERT INTO violation_date (violationId, violationDate, month, day, year) VALUES
('VIO-000001', '2024-03-15', 3,  15, 2024),
('VIO-000002', '2024-06-22', 6,  22, 2024),
('VIO-000003', '2023-11-08', 11,  8, 2023),
('VIO-000004', '2024-01-30', 1,  30, 2024),
('VIO-000005', '2023-07-19', 7,  19, 2023),
('VIO-000006', '2024-05-03', 5,   3, 2024),
('VIO-000007', '2023-09-14', 9,  14, 2023),
('VIO-000008', '2024-08-27', 8,  27, 2024),
('VIO-000009', '2022-12-05', 12,  5, 2022),
('VIO-000010', '2024-09-10', 9,  10, 2024),
('VIO-000011', '2023-04-18', 4,  18, 2023),
('VIO-000012', '2024-11-20', 11, 20, 2024),
('VIO-000013', '2023-02-14', 2,  14, 2023),
('VIO-000014', '2024-02-28', 2,  28, 2024),
('VIO-000015', '2023-10-11', 10, 11, 2023);