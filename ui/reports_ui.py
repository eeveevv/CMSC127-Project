"""
ui/reports_ui.py
LTO IMS — Reports screen Mixin (R1 – R7).
"""

from config import LICENSE_TYPES, LICENSE_STATUSES, SEX_OPTIONS
from ui.widgets import (
    _page_header, _lf, _ef, _om, _btn,
    _status_lbl, _set_status, _treeview,
)
from db import (
    report_all_drivers, report_vehicles_by_driver,
    report_expired_vehicles, report_inactive_drivers,
    report_violations_by_driver, report_violation_summary,
    report_vehicles_in_violations_by_location,
)


class ReportMixin:

    # ── Report 1 ──────────────────────────────────────────────
    def show_report1(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            f.grid_columnconfigure(3, weight=1)
            _page_header(f, "Report 1 — All Registered Drivers",
                         "Filter by type, status, age range, and sex")

            row = 1
            _lf(f, "License Type", row, 0)
            type_var, _ = _om(f, ["All"] + LICENSE_TYPES, row, 1, 220)
            _lf(f, "Status", row, 2)
            stat_var, _ = _om(f, ["All"] + LICENSE_STATUSES, row, 3, 220)
            row += 1

            _lf(f, "Sex", row, 0)
            sex_var, _ = _om(f, ["All"] + SEX_OPTIONS, row, 1, 220)
            _lf(f, "Age Min", row, 2)
            e_amin = _ef(f, row, 3, 100)
            row += 1

            _lf(f, "Age Max", row, 2)
            e_amax = _ef(f, row, 3, 100)

            stat_lbl = _status_lbl(f, row, 0, colspan=2)
            row += 1
            result = self._result_area(f, row + 1, colspan=4)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                ok, rows = report_all_drivers(
                    self.db, self.cur,
                    None if type_var.get() == "All" else type_var.get(),
                    None if stat_var.get() == "All" else stat_var.get(),
                    int(e_amin.get()) if e_amin.get().strip().isdigit() else None,
                    int(e_amax.get()) if e_amax.get().strip().isdigit() else None,
                    None if sex_var.get() == "All" else sex_var.get(),
                )
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} driver(s) found.", True)
                headers = ["Lic No", "Name", "Status", "Type",
                           "Issued", "Expires", "DOB", "Age", "Sex",
                           "Address", "City", "Region"]
                _treeview(result, headers, rows)

            _btn(f, "📊  Generate Report", run, row, 0, colspan=4)

        self._switch(build)

    # ── Report 2 ──────────────────────────────────────────────
    def show_report2(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Report 2 — Vehicles Owned by a Driver",
                         "Enter a license number to list all registered vehicles")

            _lf(f, "License Number:", 1, 0)
            e_lic = _ef(f, 1, 1)
            stat_lbl = _status_lbl(f, 2, 0)
            result = self._result_area(f, 4, colspan=2)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                try:
                    lic = int(e_lic.get().strip())
                except ValueError:
                    _set_status(stat_lbl,
                                "License number must be numeric.", False)
                    return
                ok, rows = report_vehicles_by_driver(
                    self.db, self.cur, lic)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} vehicle(s) found.", True)
                headers = ["Lic No", "Owner", "Plate",
                           "Make", "Model", "Type", "Color", "Year"]
                _treeview(result, headers, rows)

            _btn(f, "📊  Generate Report", run, 3, 0, colspan=2)

        self._switch(build)

    # ── Report 3 ──────────────────────────────────────────────
    def show_report3(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(
                f,
                "Report 3 — Vehicles with Expired Registrations",
                "Leave date blank to use today's date"
            )

            _lf(f, "As of Date (YYYY-MM-DD):", 1, 0)
            e_date = _ef(f, 1, 1, placeholder="leave blank = today")
            stat_lbl = _status_lbl(f, 2, 0)
            result = self._result_area(f, 4, colspan=2)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                date = e_date.get().strip() or None
                ok, rows = report_expired_vehicles(
                    self.db, self.cur, date)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} expired registration(s).", True)
                headers = ["Plate", "Make", "Model", "Type",
                           "Color", "Year", "Lic No",
                           "Reg No", "Reg Date", "Exp Date"]
                _treeview(result, headers, rows)

            _btn(f, "📊  Generate Report", run, 3, 0, colspan=2)

        self._switch(build)

    # ── Report 4 ──────────────────────────────────────────────
    def show_report4(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(
                f,
                "Report 4 — Inactive Drivers",
                "Drivers with Expired, Suspended, or Revoked licenses"
            )

            stat_lbl = _status_lbl(f, 2, 0)
            result = self._result_area(f, 3, colspan=2)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                ok, rows = report_inactive_drivers(self.db, self.cur)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} inactive driver(s).", True)
                headers = ["Lic No", "Name", "Status", "Type",
                           "Issued", "Expires", "DOB", "Age", "Sex",
                           "Address", "City", "Region"]
                _treeview(result, headers, rows)

            _btn(f, "📊  Generate Report", run, 1, 0, colspan=2)

        self._switch(build)

    # ── Report 5 ──────────────────────────────────────────────
    def show_report5(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Report 5 — Violations by Driver",
                         "Optionally filter by date range")

            _lf(f, "License Number *:", 1, 0)
            e_lic  = _ef(f, 1, 1)
            _lf(f, "Date From (YYYY-MM-DD):", 2, 0)
            e_from = _ef(f, 2, 1)
            _lf(f, "Date To   (YYYY-MM-DD):", 3, 0)
            e_to   = _ef(f, 3, 1)
            stat_lbl = _status_lbl(f, 4, 0)
            result = self._result_area(f, 6, colspan=2)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                try:
                    lic = int(e_lic.get().strip())
                except ValueError:
                    _set_status(stat_lbl,
                                "License number must be numeric.", False)
                    return
                ok, rows = report_violations_by_driver(
                    self.db, self.cur, lic,
                    e_from.get().strip() or None,
                    e_to.get().strip()   or None,
                )
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} violation(s) found.", True)
                headers = ["Vio ID", "Lic No", "Name", "Plate",
                           "Status", "Type", "Location",
                           "Date", "Fine (PHP)", "Officer"]
                _treeview(result, headers, rows)

            _btn(f, "📊  Generate Report", run, 5, 0, colspan=2)

        self._switch(build)

    # ── Report 6 ──────────────────────────────────────────────
    def show_report6(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(
                f,
                "Report 6 — Violation Count per Type per Year",
                "Total violations grouped by type for a given year"
            )

            _lf(f, "Year (YYYY) *:", 1, 0)
            e_year = _ef(f, 1, 1, placeholder="e.g. 2024")
            stat_lbl = _status_lbl(f, 2, 0)
            result = self._result_area(f, 4, colspan=2)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                yr = e_year.get().strip()
                if not yr.isdigit():
                    _set_status(stat_lbl,
                                "Enter a valid 4-digit year.", False)
                    return
                ok, rows = report_violation_summary(
                    self.db, self.cur, int(yr))
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} type(s) for {yr}.", True)
                headers = ["Violation Type", "Year", "Total Count"]
                _treeview(result, headers, rows,
                          col_widths=[260, 100, 120])

            _btn(f, "📊  Generate Report", run, 3, 0, colspan=2)

        self._switch(build)

    # ── Report 7 ──────────────────────────────────────────────
    def show_report7(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(
                f,
                "Report 7 — Vehicles in Violations by City / Region",
                "Leave both blank to show all; both support partial matching"
            )

            _lf(f, "City:", 1, 0)
            e_city   = _ef(f, 1, 1, placeholder="partial match OK")
            _lf(f, "Region:", 2, 0)
            e_region = _ef(f, 2, 1, placeholder="partial match OK")
            stat_lbl = _status_lbl(f, 3, 0)
            result = self._result_area(f, 5, colspan=2)

            def run():
                for w in result.winfo_children():
                    w.destroy()
                ok, rows = report_vehicles_in_violations_by_location(
                    self.db, self.cur,
                    e_city.get().strip()   or None,
                    e_region.get().strip() or None,
                )
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} vehicle(s) found.", True)
                headers = ["Plate", "Make", "Model", "Type",
                           "Color", "Year", "Owner", "City", "Region"]
                _treeview(result, headers, rows)

            _btn(f, "📊  Generate Report", run, 4, 0, colspan=2)

        self._switch(build)
