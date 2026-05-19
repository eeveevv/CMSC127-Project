"""
db/__init__.py
Aggregator — re-exports every public symbol from the sub-modules so that
the rest of the app can continue to do:

    from db import add_driver_db, get_vehicles_db, ...
"""

from db.drivers import (
    add_driver_db,
    get_drivers_db,
    edit_driver_db,
    delete_driver_db,
    upsert_driver_address_db,
)
from db.vehicles import (
    add_vehicle_db,
    get_vehicles_db,
    edit_vehicle_db,
    delete_vehicle_db,
)
from db.registrations import (
    add_registration_db,
    get_registrations_db,
    edit_registration_db,
    delete_registration_db,
)
from db.violations import (
    add_violation_db,
    get_violations_db,
    edit_violation_db,
    delete_violation_db,
)
from db.reports import (
    report_all_drivers,
    report_vehicles_by_driver,
    report_expired_vehicles,
    report_inactive_drivers,
    report_violations_by_driver,
    report_violation_summary,
    report_vehicles_in_violations_by_location,
)
from db.utils import (
    get_all_plate_numbers,
    get_all_license_numbers,
)

__all__ = [
    # drivers
    "add_driver_db", "get_drivers_db", "edit_driver_db",
    "delete_driver_db", "upsert_driver_address_db",
    # vehicles
    "add_vehicle_db", "get_vehicles_db", "edit_vehicle_db",
    "delete_vehicle_db",
    # registrations
    "add_registration_db", "get_registrations_db",
    "edit_registration_db", "delete_registration_db",
    # violations
    "add_violation_db", "get_violations_db",
    "edit_violation_db", "delete_violation_db",
    # reports
    "report_all_drivers", "report_vehicles_by_driver",
    "report_expired_vehicles", "report_inactive_drivers",
    "report_violations_by_driver", "report_violation_summary",
    "report_vehicles_in_violations_by_location",
    # utils
    "get_all_plate_numbers", "get_all_license_numbers",
]
