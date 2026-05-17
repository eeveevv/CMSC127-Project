"""
app.py
LTO Information Management System
CMSC 127 | 2nd Semester AY 2025-2026
Built with customtkinter + mysql-connector-python
"""

import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

from db_operations import (
    add_driver_db, get_drivers_db, edit_driver_db, delete_driver_db,
    upsert_driver_address_db,
    add_vehicle_db, get_vehicles_db, edit_vehicle_db, delete_vehicle_db,
    add_registration_db, get_registrations_db, edit_registration_db, delete_registration_db,
    add_violation_db, get_violations_db, edit_violation_db, delete_violation_db,
    report_all_drivers, report_vehicles_by_driver, report_expired_vehicles,
    report_inactive_drivers, report_violations_by_driver,
    report_violation_summary, report_vehicles_in_violations_by_location,
    get_all_plate_numbers, get_all_license_numbers,
)

# ── Appearance ────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "hellowrold",   # ← change if needed
    "database": "ltodata",
    "port": 3306,
}

LICENSE_TYPES   = ["Professional", "Non-Professional", "Student Permit"]
LICENSE_STATUSES = ["Valid", "Expired", "Suspended", "Revoked"]
SEX_OPTIONS     = ["Male", "Female"]
VIOLATION_STATUSES = ["Unpaid", "Paid", "Contested"]
REG_STATUSES    = ["Active", "Expired", "Suspended"]
VEHICLE_TYPES   = ["Private Car", "Motorcycle", "Public Utility Vehicle", "Truck", "Bus"]


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════

def _table(parent, headers, rows, col_widths=None):
    """Render a simple fixed-width table inside a CTkTextbox."""
    box = ctk.CTkTextbox(parent, font=("Courier New", 12), wrap="none")
    box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    if col_widths is None:
        col_widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
                      for i, h in enumerate(headers)]

    header = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    sep    = "-" * (sum(col_widths) + 3 * (len(headers) - 1))
    box.insert("end", header + "\n" + sep + "\n")
    for row in rows:
        line = " | ".join(str(row[i] if row[i] is not None else "").ljust(col_widths[i])
                          for i in range(len(headers)))
        box.insert("end", line + "\n")
    box.configure(state="disabled")
    return box


def _lf(parent, text, row, col, **kw):
    ctk.CTkLabel(parent, text=text).grid(row=row, column=col, sticky="w",
                                         padx=8, pady=4, **kw)


def _ef(parent, row, col, width=260, **kw):
    e = ctk.CTkEntry(parent, width=width, **kw)
    e.grid(row=row, column=col, padx=8, pady=4, sticky="ew")
    return e


def _om(parent, values, row, col, width=260):
    var = ctk.StringVar(value=values[0])
    m = ctk.CTkOptionMenu(parent, values=values, variable=var, width=width)
    m.grid(row=row, column=col, padx=8, pady=4, sticky="ew")
    return var, m


def _btn(parent, text, cmd, row, col, colspan=1, color=None):
    kw = {}
    if color:
        kw["fg_color"] = color
        kw["hover_color"] = "#8B0000" if color == "red" else None
    b = ctk.CTkButton(parent, text=text, command=cmd, **kw)
    b.grid(row=row, column=col, columnspan=colspan, padx=8, pady=6, sticky="ew")
    return b


def _status(parent, row, col, colspan=2):
    lbl = ctk.CTkLabel(parent, text="")
    lbl.grid(row=row, column=col, columnspan=colspan, pady=4)
    return lbl


def _set_status(lbl, msg, ok=True):
    lbl.configure(text=msg, text_color="#4CAF50" if ok else "#F44336")


# ══════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════

class LTOApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LTO Information Management System")
        self.geometry("1280x820")
        self.minsize(1100, 700)

        self.db  = None
        self.cur = None
        self._connect()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._current = None
        self.show_dashboard()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── DB connect ────────────────────────────
    def _connect(self):
        try:
            self.db  = mysql.connector.connect(**DB_CONFIG)
            self.cur = self.db.cursor()
        except Error as e:
            messagebox.showerror("Connection Error",
                f"Could not connect to MySQL:\n{e}\n\n"
                "Check DB_CONFIG at the top of app.py.")

    def _on_close(self):
        if self.db and self.db.is_connected():
            self.cur.close()
            self.db.close()
        self.destroy()

    # ── Sidebar ───────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=210, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        ctk.CTkLabel(sb, text="🚗 LTO System",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))

        sections = [
            ("── DRIVERS ──",     None),
            ("Add Driver",        self.show_add_driver),
            ("View / Search",     self.show_view_drivers),
            ("Edit Driver",       self.show_edit_driver),
            ("Delete Driver",     self.show_delete_driver),
            ("── VEHICLES ──",    None),
            ("Add Vehicle",       self.show_add_vehicle),
            ("View / Search",     self.show_view_vehicles),
            ("Edit Vehicle",      self.show_edit_vehicle),
            ("Delete Vehicle",    self.show_delete_vehicle),
            ("── REGISTRATIONS ──", None),
            ("Add Registration",  self.show_add_registration),
            ("View / Search",     self.show_view_registrations),
            ("Edit Registration", self.show_edit_registration),
            ("Delete Registration", self.show_delete_registration),
            ("── VIOLATIONS ──",  None),
            ("Add Violation",     self.show_add_violation),
            ("View / Search",     self.show_view_violations),
            ("Edit Violation",    self.show_edit_violation),
            ("Delete Violation",  self.show_delete_violation),
            ("── REPORTS ──",     None),
            ("R1: All Drivers",   self.show_report1),
            ("R2: Driver Vehicles", self.show_report2),
            ("R3: Expired Reg.",  self.show_report3),
            ("R4: Inactive Drivers", self.show_report4),
            ("R5: Driver Violations", self.show_report5),
            ("R6: Violation Summary", self.show_report6),
            ("R7: Violations by Location", self.show_report7),
        ]

        scroll = ctk.CTkScrollableFrame(sb, width=190)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        for label, cmd in sections:
            if cmd is None:
                ctk.CTkLabel(scroll, text=label,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color="gray").pack(pady=(10, 2), padx=5, anchor="w")
            else:
                ctk.CTkButton(scroll, text=label, command=cmd,
                              height=28, anchor="w").pack(
                    fill="x", padx=5, pady=2)

    # ── View switcher ─────────────────────────
    def _switch(self, builder):
        if self._current:
            self._current.destroy()
        self._current = ctk.CTkFrame(self.content, corner_radius=0)
        self._current.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self._current.grid_columnconfigure(1, weight=1)
        builder(self._current)

    # ═══════════════════════════════════════════
    # DASHBOARD
    # ═══════════════════════════════════════════
    def show_dashboard(self):
        def build(f):
            ctk.CTkLabel(f, text="LTO Information Management System",
                         font=ctk.CTkFont(size=26, weight="bold")).pack(pady=30)
            if not (self.db and self.db.is_connected()):
                ctk.CTkLabel(f, text="⚠ Not connected to database.",
                             text_color="red").pack()
                return
            try:
                counts = {}
                for tbl in ("driver", "vehicle", "registration", "violation"):
                    self.cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                    counts[tbl] = self.cur.fetchone()[0]

                grid = ctk.CTkFrame(f)
                grid.pack(pady=10)
                tiles = [("Drivers",       counts["driver"],       "#1976D2"),
                         ("Vehicles",      counts["vehicle"],      "#388E3C"),
                         ("Registrations", counts["registration"], "#F57C00"),
                         ("Violations",    counts["violation"],    "#D32F2F")]
                for i, (title, val, col) in enumerate(tiles):
                    tile = ctk.CTkFrame(grid, fg_color=col, corner_radius=12,
                                        width=180, height=100)
                    tile.grid(row=0, column=i, padx=12, pady=12)
                    tile.grid_propagate(False)
                    ctk.CTkLabel(tile, text=str(val),
                                 font=ctk.CTkFont(size=36, weight="bold"),
                                 text_color="white").place(relx=0.5, rely=0.38, anchor="center")
                    ctk.CTkLabel(tile, text=title,
                                 font=ctk.CTkFont(size=13),
                                 text_color="white").place(relx=0.5, rely=0.72, anchor="center")

                ctk.CTkLabel(f, text="Use the sidebar to navigate.",
                             font=ctk.CTkFont(size=14, slant="italic"),
                             text_color="gray").pack(pady=20)
            except Exception as e:
                ctk.CTkLabel(f, text=f"Error: {e}", text_color="red").pack()
        self._switch(build)

    # ═══════════════════════════════════════════
    # DRIVER VIEWS
    # ═══════════════════════════════════════════
    def show_add_driver(self):
        def build(f):
            ctk.CTkLabel(f, text="Add New Driver",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=15)

            fields = [
                ("License Number:",         "licenseNumber"),
                ("Full Name:",              "fullName"),
                ("Date of Birth (YYYY-MM-DD):", "dateOfBirth"),
            ]
            entries = {}
            for i, (lbl, key) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1)

            _lf(f, "Sex:", len(fields)+1, 0)
            sex_var, _ = _om(f, SEX_OPTIONS, len(fields)+1, 1)

            _lf(f, "License Type:", len(fields)+2, 0)
            type_var, _ = _om(f, LICENSE_TYPES, len(fields)+2, 1)

            _lf(f, "License Status:", len(fields)+3, 0)
            status_var, _ = _om(f, LICENSE_STATUSES, len(fields)+3, 1)

            _lf(f, "Issuance Date (YYYY-MM-DD):", len(fields)+4, 0)
            entries["licenseIssuanceDate"] = _ef(f, len(fields)+4, 1)

            _lf(f, "Expiration Date (YYYY-MM-DD):", len(fields)+5, 0)
            entries["licenseExpirationDate"] = _ef(f, len(fields)+5, 1)

            ctk.CTkLabel(f, text="── Address (optional) ──",
                         text_color="gray").grid(row=len(fields)+6, column=0,
                                                  columnspan=2, pady=(10, 2))
            _lf(f, "Address:", len(fields)+7, 0)
            entries["address"] = _ef(f, len(fields)+7, 1)
            _lf(f, "City:", len(fields)+8, 0)
            entries["city"] = _ef(f, len(fields)+8, 1)
            _lf(f, "Region:", len(fields)+9, 0)
            entries["region"] = _ef(f, len(fields)+9, 1)

            stat = _status(f, len(fields)+11, 0)

            def submit():
                ok, msg = add_driver_db(
                    self.db, self.cur,
                    entries["licenseNumber"].get().strip(),
                    entries["fullName"].get().strip(),
                    status_var.get(), type_var.get(),
                    entries["licenseIssuanceDate"].get().strip(),
                    entries["licenseExpirationDate"].get().strip(),
                    entries["dateOfBirth"].get().strip(),
                    sex_var.get()
                )
                _set_status(stat, msg, ok)
                if ok:
                    addr = entries["address"].get().strip()
                    city = entries["city"].get().strip()
                    reg  = entries["region"].get().strip()
                    if addr and city and reg:
                        upsert_driver_address_db(self.db, self.cur,
                            int(entries["licenseNumber"].get()), addr, city, reg)
                    for e in entries.values():
                        e.delete(0, "end")

            _btn(f, "Add Driver", submit, len(fields)+10, 0, colspan=2)

        self._switch(build)

    def show_view_drivers(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text="View / Search Drivers",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=4, pady=12)

            _lf(f, "License No.:", 1, 0)
            e_lic = _ef(f, 1, 1, 140)
            _lf(f, "Name:", 1, 2)
            e_name = _ef(f, 1, 3, 140)

            _lf(f, "License Type:", 2, 0)
            type_var, _ = _om(f, ["All"] + LICENSE_TYPES, 2, 1, 160)
            _lf(f, "Status:", 2, 2)
            stat_var, _ = _om(f, ["All"] + LICENSE_STATUSES, 2, 3, 160)

            _lf(f, "Sex:", 3, 0)
            sex_var, _ = _om(f, ["All"] + SEX_OPTIONS, 3, 1, 160)
            _lf(f, "Age min:", 3, 2)
            e_amin = _ef(f, 3, 3, 80)

            _lf(f, "Age max:", 4, 2)
            e_amax = _ef(f, 4, 3, 80)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=6, column=0, columnspan=4, sticky="nsew",
                              padx=8, pady=8)
            f.grid_rowconfigure(6, weight=1)

            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=5, column=0, columnspan=4)

            def search():
                for w in result_frame.winfo_children():
                    w.destroy()
                criteria = {}
                if e_lic.get().strip():
                    try:
                        criteria['licenseNumber'] = int(e_lic.get().strip())
                    except ValueError:
                        _set_status(stat_lbl, "License number must be numeric.", False)
                        return
                if e_name.get().strip():
                    criteria['fullName'] = e_name.get().strip()
                if type_var.get() != "All":
                    criteria['licenseType'] = type_var.get()
                if stat_var.get() != "All":
                    criteria['licenseStatus'] = stat_var.get()
                if sex_var.get() != "All":
                    criteria['sex'] = sex_var.get()
                if e_amin.get().strip():
                    criteria['age_min'] = int(e_amin.get().strip())
                if e_amax.get().strip():
                    criteria['age_max'] = int(e_amax.get().strip())

                ok, rows = get_drivers_db(self.db, self.cur, criteria)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl, f"{len(rows)} record(s) found.", True)
                headers = ["LicNo", "Full Name", "Status", "Type",
                           "Issued", "Expires", "DOB", "Age", "Sex",
                           "Address", "City", "Region"]
                _table(result_frame, headers, rows)

            _btn(f, "Search", search, 4, 0, colspan=2)
            _btn(f, "View All", lambda: (
                e_lic.delete(0, "end"), e_name.delete(0, "end"),
                type_var.set("All"), stat_var.set("All"),
                sex_var.set("All"), e_amin.delete(0, "end"),
                e_amax.delete(0, "end"), search()
            ), 4, 2, colspan=2)

        self._switch(build)

    def show_edit_driver(self):
        def build(f):
            ctk.CTkLabel(f, text="Edit Driver",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)

            _lf(f, "License Number to edit:", 1, 0)
            e_lic = _ef(f, 1, 1)
            stat  = _status(f, 2, 0)

            inner = ctk.CTkFrame(f)
            inner.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
            inner.grid_columnconfigure(1, weight=1)

            entries  = {}
            vars_map = {}

            def load():
                for w in inner.winfo_children():
                    w.destroy()
                entries.clear(); vars_map.clear()
                try:
                    lic = int(e_lic.get().strip())
                except ValueError:
                    _set_status(stat, "License number must be numeric.", False)
                    return
                ok, rows = get_drivers_db(self.db, self.cur, {'licenseNumber': lic})
                if not ok or not rows:
                    _set_status(stat, "Driver not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[1]}", True)

                edit_fields = [
                    ("Full Name",           "fullName",            r[1]),
                    ("Issuance Date",       "licenseIssuanceDate", str(r[4])),
                    ("Expiration Date",     "licenseExpirationDate", str(r[5])),
                    ("Date of Birth",       "dateOfBirth",         str(r[6])),
                    ("Address",             "_addr",               str(r[9] or "")),
                    ("City",                "_city",               str(r[10] or "")),
                    ("Region",              "_region",             str(r[11] or "")),
                ]
                for i, (lbl, key, val) in enumerate(edit_fields):
                    _lf(inner, lbl + ":", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Sex:", len(edit_fields), 0)
                sv, _ = _om(inner, SEX_OPTIONS, len(edit_fields), 1)
                sv.set(r[8])
                vars_map["sex"] = sv

                _lf(inner, "License Type:", len(edit_fields)+1, 0)
                tv, _ = _om(inner, LICENSE_TYPES, len(edit_fields)+1, 1)
                tv.set(r[3])
                vars_map["licenseType"] = tv

                _lf(inner, "License Status:", len(edit_fields)+2, 0)
                stv, _ = _om(inner, LICENSE_STATUSES, len(edit_fields)+2, 1)
                stv.set(r[2])
                vars_map["licenseStatus"] = stv

                def save():
                    updates = {}
                    for key, widget in entries.items():
                        if not key.startswith("_"):
                            val = widget.get().strip()
                            if val:
                                updates[key] = val
                    updates["sex"]           = vars_map["sex"].get()
                    updates["licenseType"]   = vars_map["licenseType"].get()
                    updates["licenseStatus"] = vars_map["licenseStatus"].get()

                    ok2, msg = edit_driver_db(self.db, self.cur, lic, updates)
                    _set_status(stat, msg, ok2)

                    addr   = entries["_addr"].get().strip()
                    city   = entries["_city"].get().strip()
                    region = entries["_region"].get().strip()
                    if addr and city and region:
                        upsert_driver_address_db(self.db, self.cur, lic, addr, city, region)

                _btn(inner, "Save Changes", save, len(edit_fields)+3, 0, colspan=2)

            _btn(f, "Load Driver", load, 1, 1)

        self._switch(build)

    def show_delete_driver(self):
        def build(f):
            ctk.CTkLabel(f, text="Delete Driver",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "License Number:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm", "Delete this driver? This cannot be undone."):
                    return
                try:
                    lic = int(e.get().strip())
                except ValueError:
                    _set_status(stat, "License number must be numeric.", False)
                    return
                ok, msg = delete_driver_db(self.db, self.cur, lic)
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "Delete Driver", delete, 2, 0, colspan=2, color="red")
        self._switch(build)

    # ═══════════════════════════════════════════
    # VEHICLE VIEWS
    # ═══════════════════════════════════════════
    def show_add_vehicle(self):
        def build(f):
            ctk.CTkLabel(f, text="Add New Vehicle",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)

            fields = [
                ("Plate Number:",    "plateNumber"),
                ("Engine Number:",   "engineNumber"),
                ("Chassis Number:",  "chassisNumber"),
                ("Make:",            "make"),
                ("Model:",           "model"),
                ("Color:",           "color"),
                ("Year (YYYY):",     "year"),
                ("License Number (owner):", "licenseNumber"),
            ]
            entries = {}
            for i, (lbl, key) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1)

            _lf(f, "Vehicle Type:", len(fields)+1, 0)
            type_var, _ = _om(f, VEHICLE_TYPES, len(fields)+1, 1)

            stat = _status(f, len(fields)+3, 0)

            def submit():
                try:
                    yr  = int(entries["year"].get().strip())
                    lic = int(entries["licenseNumber"].get().strip())
                except ValueError:
                    _set_status(stat, "Year and License Number must be numeric.", False)
                    return
                ok, msg = add_vehicle_db(
                    self.db, self.cur,
                    entries["plateNumber"].get().strip(),
                    entries["engineNumber"].get().strip(),
                    entries["chassisNumber"].get().strip(),
                    entries["make"].get().strip(),
                    entries["model"].get().strip(),
                    entries["color"].get().strip(),
                    type_var.get(), yr, lic
                )
                _set_status(stat, msg, ok)
                if ok:
                    for e in entries.values():
                        e.delete(0, "end")

            _btn(f, "Add Vehicle", submit, len(fields)+2, 0, colspan=2)
        self._switch(build)

    def show_view_vehicles(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text="View / Search Vehicles",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=4, pady=12)

            _lf(f, "Plate Number:", 1, 0)
            e_plate = _ef(f, 1, 1, 160)
            _lf(f, "License No.:", 1, 2)
            e_lic = _ef(f, 1, 3, 160)
            _lf(f, "Make:", 2, 0)
            e_make = _ef(f, 2, 1, 160)
            _lf(f, "Type:", 2, 2)
            type_var, _ = _om(f, ["All"] + VEHICLE_TYPES, 2, 3, 160)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(5, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=4, column=0, columnspan=4)

            def search():
                for w in result_frame.winfo_children():
                    w.destroy()
                criteria = {}
                if e_plate.get().strip(): criteria['plateNumber']   = e_plate.get().strip()
                if e_make.get().strip():  criteria['make']          = e_make.get().strip()
                if type_var.get() != "All": criteria['type']        = type_var.get()
                if e_lic.get().strip():
                    try:
                        criteria['licenseNumber'] = int(e_lic.get().strip())
                    except ValueError:
                        _set_status(stat_lbl, "License number must be numeric.", False)
                        return
                ok, rows = get_vehicles_db(self.db, self.cur, criteria)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl, f"{len(rows)} record(s) found.", True)
                headers = ["Plate", "Engine", "Chassis", "Make", "Model",
                           "Color", "Type", "Year", "LicNo", "Owner"]
                _table(result_frame, headers, rows)

            _btn(f, "Search", search, 3, 0, colspan=2)
            _btn(f, "View All", lambda: (
                e_plate.delete(0, "end"), e_lic.delete(0, "end"),
                e_make.delete(0, "end"), type_var.set("All"), search()
            ), 3, 2, colspan=2)
        self._switch(build)

    def show_edit_vehicle(self):
        def build(f):
            ctk.CTkLabel(f, text="Edit Vehicle",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Plate Number to edit:", 1, 0)
            e_plate = _ef(f, 1, 1)
            stat = _status(f, 2, 0)
            inner = ctk.CTkFrame(f)
            inner.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8)
            inner.grid_columnconfigure(1, weight=1)
            entries = {}
            vars_map = {}

            def load():
                for w in inner.winfo_children():
                    w.destroy()
                entries.clear(); vars_map.clear()
                plate = e_plate.get().strip()
                if not plate:
                    _set_status(stat, "Enter a plate number.", False)
                    return
                ok, rows = get_vehicles_db(self.db, self.cur, {'plateNumber': plate})
                if not ok or not rows:
                    _set_status(stat, "Vehicle not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[3]} {r[4]} ({r[0]})", True)

                edit_fields = [
                    ("Make",   "make",   r[3]),
                    ("Model",  "model",  r[4]),
                    ("Color",  "color",  r[5]),
                    ("Year",   "year",   str(r[7])),
                ]
                for i, (lbl, key, val) in enumerate(edit_fields):
                    _lf(inner, lbl + ":", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Type:", len(edit_fields), 0)
                tv, _ = _om(inner, VEHICLE_TYPES, len(edit_fields), 1)
                tv.set(r[6])
                vars_map["type"] = tv

                def save():
                    updates = {k: v.get().strip() for k, v in entries.items() if v.get().strip()}
                    updates["type"] = vars_map["type"].get()
                    if "year" in updates:
                        try:
                            updates["year"] = int(updates["year"])
                        except ValueError:
                            _set_status(stat, "Year must be numeric.", False)
                            return
                    ok2, msg = edit_vehicle_db(self.db, self.cur, plate, updates)
                    _set_status(stat, msg, ok2)

                _btn(inner, "Save Changes", save, len(edit_fields)+1, 0, colspan=2)

            _btn(f, "Load Vehicle", load, 1, 1)
        self._switch(build)

    def show_delete_vehicle(self):
        def build(f):
            ctk.CTkLabel(f, text="Delete Vehicle",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Plate Number:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm", "Delete this vehicle?"):
                    return
                ok, msg = delete_vehicle_db(self.db, self.cur, e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "Delete Vehicle", delete, 2, 0, colspan=2, color="red")
        self._switch(build)

    # ═══════════════════════════════════════════
    # REGISTRATION VIEWS
    # ═══════════════════════════════════════════
    def show_add_registration(self):
        def build(f):
            ctk.CTkLabel(f, text="Add Registration",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            fields = [
                ("Registration Number:", "registrationNumber"),
                ("Plate Number:",        "plateNumber"),
                ("Registration Date (YYYY-MM-DD):", "registrationDate"),
                ("Expiration Date (YYYY-MM-DD):",   "expirationDate"),
            ]
            entries = {}
            for i, (lbl, key) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1)

            _lf(f, "Status:", len(fields)+1, 0)
            status_var, _ = _om(f, REG_STATUSES, len(fields)+1, 1)
            stat = _status(f, len(fields)+3, 0)

            def submit():
                ok, msg = add_registration_db(
                    self.db, self.cur,
                    entries["registrationNumber"].get().strip(),
                    entries["plateNumber"].get().strip(),
                    status_var.get(),
                    entries["registrationDate"].get().strip(),
                    entries["expirationDate"].get().strip(),
                )
                _set_status(stat, msg, ok)
                if ok:
                    for e in entries.values():
                        e.delete(0, "end")

            _btn(f, "Add Registration", submit, len(fields)+2, 0, colspan=2)
        self._switch(build)

    def show_view_registrations(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text="View / Search Registrations",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Plate Number (leave blank for all):", 1, 0)
            e_plate = _ef(f, 1, 1)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(4, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=3, column=0, columnspan=2)

            def search():
                for w in result_frame.winfo_children():
                    w.destroy()
                plate = e_plate.get().strip() or None
                ok, rows = get_registrations_db(self.db, self.cur, plate)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl, f"{len(rows)} record(s) found.", True)
                headers = ["RegNo", "Plate", "Status", "Reg Date", "Exp Date", "Make", "Model"]
                _table(result_frame, headers, rows)

            _btn(f, "Search", search, 2, 0)
            _btn(f, "View All", lambda: (e_plate.delete(0, "end"), search()), 2, 1)
        self._switch(build)

    def show_edit_registration(self):
        def build(f):
            ctk.CTkLabel(f, text="Edit Registration",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Registration Number to edit:", 1, 0)
            e_reg = _ef(f, 1, 1)
            stat = _status(f, 2, 0)
            inner = ctk.CTkFrame(f)
            inner.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8)
            inner.grid_columnconfigure(1, weight=1)
            entries = {}
            vars_map = {}

            def load():
                for w in inner.winfo_children():
                    w.destroy()
                entries.clear(); vars_map.clear()
                reg_no = e_reg.get().strip()
                if not reg_no:
                    _set_status(stat, "Enter a registration number.", False)
                    return
                ok, rows = get_registrations_db(self.db, self.cur)
                rows = [r for r in rows if r[0] == reg_no] if ok else []
                if not rows:
                    _set_status(stat, "Registration not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[0]}", True)

                edit_fields = [
                    ("Registration Date", "registrationDate", str(r[3])),
                    ("Expiration Date",   "expirationDate",   str(r[4])),
                ]
                for i, (lbl, key, val) in enumerate(edit_fields):
                    _lf(inner, lbl + " (YYYY-MM-DD):", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Status:", len(edit_fields), 0)
                sv, _ = _om(inner, REG_STATUSES, len(edit_fields), 1)
                sv.set(r[2])
                vars_map["status"] = sv

                def save():
                    updates = {k: v.get().strip() for k, v in entries.items() if v.get().strip()}
                    updates["status"] = vars_map["status"].get()
                    ok2, msg = edit_registration_db(self.db, self.cur, reg_no, updates)
                    _set_status(stat, msg, ok2)

                _btn(inner, "Save Changes", save, len(edit_fields)+1, 0, colspan=2)

            _btn(f, "Load Registration", load, 1, 1)
        self._switch(build)

    def show_delete_registration(self):
        def build(f):
            ctk.CTkLabel(f, text="Delete Registration",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Registration Number:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm", "Delete this registration?"):
                    return
                ok, msg = delete_registration_db(self.db, self.cur, e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "Delete Registration", delete, 2, 0, colspan=2, color="red")
        self._switch(build)

    # ═══════════════════════════════════════════
    # VIOLATION VIEWS
    # ═══════════════════════════════════════════
    def show_add_violation(self):
        def build(f):
            ctk.CTkLabel(f, text="Add Violation",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            fields = [
                ("Violation ID:",             "violationId"),
                ("License Number:",           "licenseNumber"),
                ("Plate Number:",             "plateNumber"),
                ("Violation Type:",           "type"),
                ("Location:",                 "location"),
                ("Violation Date (YYYY-MM-DD):", "violationDate"),
                ("Fine Amount (PHP):",        "fineAmount"),
                ("Apprehending Officer (opt.):", "apprehendingOfficer"),
            ]
            entries = {}
            for i, (lbl, key) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1)

            _lf(f, "Status:", len(fields)+1, 0)
            status_var, _ = _om(f, VIOLATION_STATUSES, len(fields)+1, 1)
            stat = _status(f, len(fields)+3, 0)

            def submit():
                try:
                    lic  = int(entries["licenseNumber"].get().strip())
                    fine = float(entries["fineAmount"].get().strip())
                except ValueError:
                    _set_status(stat, "License number must be integer; fine must be a number.", False)
                    return
                ok, msg = add_violation_db(
                    self.db, self.cur,
                    entries["violationId"].get().strip(), lic,
                    entries["plateNumber"].get().strip(),
                    status_var.get(),
                    entries["type"].get().strip(),
                    entries["location"].get().strip(),
                    entries["violationDate"].get().strip(),
                    fine,
                    entries["apprehendingOfficer"].get().strip() or None
                )
                _set_status(stat, msg, ok)
                if ok:
                    for e in entries.values():
                        e.delete(0, "end")

            _btn(f, "Add Violation", submit, len(fields)+2, 0, colspan=2)
        self._switch(build)

    def show_view_violations(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text="View / Search Violations",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=4, pady=12)

            _lf(f, "License No.:", 1, 0)
            e_lic = _ef(f, 1, 1, 160)
            _lf(f, "Plate No.:", 1, 2)
            e_plate = _ef(f, 1, 3, 160)
            _lf(f, "Status:", 2, 0)
            stat_var, _ = _om(f, ["All"] + VIOLATION_STATUSES, 2, 1, 160)
            _lf(f, "Date From:", 2, 2)
            e_from = _ef(f, 2, 3, 160)
            _lf(f, "Date To:", 3, 2)
            e_to = _ef(f, 3, 3, 160)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(6, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=5, column=0, columnspan=4)

            def search():
                for w in result_frame.winfo_children():
                    w.destroy()
                criteria = {}
                if e_lic.get().strip():
                    try:
                        criteria['licenseNumber'] = int(e_lic.get().strip())
                    except ValueError:
                        _set_status(stat_lbl, "License number must be numeric.", False)
                        return
                if e_plate.get().strip():  criteria['plateNumber'] = e_plate.get().strip()
                if stat_var.get() != "All": criteria['status']     = stat_var.get()
                if e_from.get().strip():   criteria['date_from']   = e_from.get().strip()
                if e_to.get().strip():     criteria['date_to']     = e_to.get().strip()

                ok, rows = get_violations_db(self.db, self.cur, criteria)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl, f"{len(rows)} record(s) found.", True)
                headers = ["VioID", "LicNo", "Name", "Plate", "Status",
                           "Type", "Location", "Date", "Fine", "Officer"]
                _table(result_frame, headers, rows)

            _btn(f, "Search", search, 4, 0, colspan=2)
            _btn(f, "View All", lambda: (
                e_lic.delete(0,"end"), e_plate.delete(0,"end"),
                stat_var.set("All"), e_from.delete(0,"end"),
                e_to.delete(0,"end"), search()
            ), 4, 2, colspan=2)
        self._switch(build)

    def show_edit_violation(self):
        def build(f):
            ctk.CTkLabel(f, text="Edit Violation",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Violation ID to edit:", 1, 0)
            e_vid = _ef(f, 1, 1)
            stat = _status(f, 2, 0)
            inner = ctk.CTkFrame(f)
            inner.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8)
            inner.grid_columnconfigure(1, weight=1)
            entries = {}
            vars_map = {}

            def load():
                for w in inner.winfo_children():
                    w.destroy()
                entries.clear(); vars_map.clear()
                vid = e_vid.get().strip()
                if not vid:
                    _set_status(stat, "Enter a violation ID.", False)
                    return
                ok, rows = get_violations_db(self.db, self.cur, {})
                rows = [r for r in rows if r[0] == vid] if ok else []
                if not rows:
                    _set_status(stat, "Violation not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[0]}", True)

                edit_fields = [
                    ("Type",       "type",                str(r[5])),
                    ("Location",   "location",            str(r[6])),
                    ("Fine Amount","fineAmount",           str(r[8])),
                    ("Officer",    "apprehendingOfficer",  str(r[9] or "")),
                ]
                for i, (lbl, key, val) in enumerate(edit_fields):
                    _lf(inner, lbl + ":", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Status:", len(edit_fields), 0)
                sv, _ = _om(inner, VIOLATION_STATUSES, len(edit_fields), 1)
                sv.set(r[4])
                vars_map["status"] = sv

                def save():
                    updates = {k: v.get().strip() for k, v in entries.items() if v.get().strip()}
                    updates["status"] = vars_map["status"].get()
                    if "fineAmount" in updates:
                        try:
                            updates["fineAmount"] = float(updates["fineAmount"])
                        except ValueError:
                            _set_status(stat, "Fine amount must be numeric.", False)
                            return
                    ok2, msg = edit_violation_db(self.db, self.cur, vid, updates)
                    _set_status(stat, msg, ok2)

                _btn(inner, "Save Changes", save, len(edit_fields)+1, 0, colspan=2)

            _btn(f, "Load Violation", load, 1, 1)
        self._switch(build)

    def show_delete_violation(self):
        def build(f):
            ctk.CTkLabel(f, text="Delete Violation",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Violation ID:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm", "Delete this violation?"):
                    return
                ok, msg = delete_violation_db(self.db, self.cur, e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "Delete Violation", delete, 2, 0, colspan=2, color="red")
        self._switch(build)

    # ═══════════════════════════════════════════
    # REPORT VIEWS
    # ═══════════════════════════════════════════
    def _report_frame(self, title):
        frame = [None]
        def build(f):
            ctk.CTkLabel(f, text=title,
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=4, pady=12)
            frame[0] = f
        self._switch(build)
        return frame[0]

    def show_report1(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 1 — All Registered Drivers",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=4, pady=12)

            _lf(f, "License Type:", 1, 0)
            type_var, _ = _om(f, ["All"] + LICENSE_TYPES, 1, 1, 160)
            _lf(f, "Status:", 1, 2)
            stat_var, _ = _om(f, ["All"] + LICENSE_STATUSES, 1, 3, 160)
            _lf(f, "Sex:", 2, 0)
            sex_var, _ = _om(f, ["All"] + SEX_OPTIONS, 2, 1, 160)
            _lf(f, "Age min:", 2, 2)
            e_amin = _ef(f, 2, 3, 80)
            _lf(f, "Age max:", 3, 2)
            e_amax = _ef(f, 3, 3, 80)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(6, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=5, column=0, columnspan=4)

            def run():
                for w in result_frame.winfo_children():
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
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} driver(s) found.", True)
                headers = ["LicNo", "Name", "Status", "Type",
                           "Issued", "Expires", "DOB", "Age", "Sex",
                           "Address", "City", "Region"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 4, 0, colspan=4)
        self._switch(build)

    def show_report2(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 2 — Vehicles Owned by a Driver",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "License Number:", 1, 0)
            e_lic = _ef(f, 1, 1)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(4, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=3, column=0, columnspan=2)

            def run():
                for w in result_frame.winfo_children():
                    w.destroy()
                try:
                    lic = int(e_lic.get().strip())
                except ValueError:
                    _set_status(stat_lbl, "License number must be numeric.", False)
                    return
                ok, rows = report_vehicles_by_driver(self.db, self.cur, lic)
                if not ok:
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} vehicle(s) found.", True)
                headers = ["LicNo", "Owner", "Plate", "Make", "Model", "Type", "Color", "Year"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 2, 0, colspan=2)
        self._switch(build)

    def show_report3(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 3 — Vehicles with Expired Registrations",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "As of date (YYYY-MM-DD, blank=today):", 1, 0)
            e_date = _ef(f, 1, 1)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(4, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=3, column=0, columnspan=2)

            def run():
                for w in result_frame.winfo_children():
                    w.destroy()
                date = e_date.get().strip() or None
                ok, rows = report_expired_vehicles(self.db, self.cur, date)
                if not ok:
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} expired registration(s).", True)
                headers = ["Plate", "Make", "Model", "Type", "Color", "Year",
                           "LicNo", "RegNo", "Reg Date", "Exp Date"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 2, 0, colspan=2)
        self._switch(build)

    def show_report4(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 4 — Inactive Drivers (Expired / Suspended / Revoked)",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(3, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=2, column=0, columnspan=2)

            def run():
                for w in result_frame.winfo_children():
                    w.destroy()
                ok, rows = report_inactive_drivers(self.db, self.cur)
                if not ok:
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} inactive driver(s).", True)
                headers = ["LicNo", "Name", "Status", "Type",
                           "Issued", "Expires", "DOB", "Age", "Sex",
                           "Address", "City", "Region"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 1, 0, colspan=2)
        self._switch(build)

    def show_report5(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 5 — Violations by Driver within Date Range",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "License Number:", 1, 0)
            e_lic = _ef(f, 1, 1)
            _lf(f, "Date From (YYYY-MM-DD):", 2, 0)
            e_from = _ef(f, 2, 1)
            _lf(f, "Date To   (YYYY-MM-DD):", 3, 0)
            e_to = _ef(f, 3, 1)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(6, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=5, column=0, columnspan=2)

            def run():
                for w in result_frame.winfo_children():
                    w.destroy()
                try:
                    lic = int(e_lic.get().strip())
                except ValueError:
                    _set_status(stat_lbl, "License number must be numeric.", False)
                    return
                ok, rows = report_violations_by_driver(
                    self.db, self.cur, lic,
                    e_from.get().strip() or None,
                    e_to.get().strip() or None,
                )
                if not ok:
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} violation(s) found.", True)
                headers = ["VioID", "LicNo", "Name", "Plate", "Status",
                           "Type", "Location", "Date", "Fine", "Officer"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 4, 0, colspan=2)
        self._switch(build)

    def show_report6(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 6 — Violation Count per Type per Year",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "Year (YYYY):", 1, 0)
            e_year = _ef(f, 1, 1)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(4, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=3, column=0, columnspan=2)

            def run():
                for w in result_frame.winfo_children():
                    w.destroy()
                yr = e_year.get().strip()
                if not yr.isdigit():
                    _set_status(stat_lbl, "Enter a valid 4-digit year.", False)
                    return
                ok, rows = report_violation_summary(self.db, self.cur, int(yr))
                if not ok:
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} type(s) for {yr}.", True)
                headers = ["Violation Type", "Year", "Total Count"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 2, 0, colspan=2)
        self._switch(build)

    def show_report7(self):
        def build(f):
            ctk.CTkLabel(f, text="Report 7 — Vehicles in Violations by City / Region",
                         font=ctk.CTkFont(size=20, weight="bold")).grid(
                row=0, column=0, columnspan=2, pady=12)
            _lf(f, "City (leave blank to skip):", 1, 0)
            e_city = _ef(f, 1, 1)
            _lf(f, "Region (leave blank to skip):", 2, 0)
            e_region = _ef(f, 2, 1)

            result_frame = ctk.CTkFrame(f)
            result_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
            f.grid_rowconfigure(5, weight=1)
            stat_lbl = ctk.CTkLabel(f, text="")
            stat_lbl.grid(row=4, column=0, columnspan=2)

            def run():
                for w in result_frame.winfo_children():
                    w.destroy()
                ok, rows = report_vehicles_in_violations_by_location(
                    self.db, self.cur,
                    e_city.get().strip() or None,
                    e_region.get().strip() or None,
                )
                if not ok:
                    _set_status(stat_lbl, rows, False); return
                _set_status(stat_lbl, f"{len(rows)} vehicle(s) found.", True)
                headers = ["Plate", "Make", "Model", "Type", "Color", "Year",
                           "Owner", "City", "Region"]
                _table(result_frame, headers, rows)

            _btn(f, "Generate Report", run, 3, 0, colspan=2)
        self._switch(build)


# ══════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = LTOApp()
    app.mainloop()