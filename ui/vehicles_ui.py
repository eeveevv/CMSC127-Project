"""
ui/vehicles_ui.py
LTO IMS — Vehicle screen Mixin (Add / View / Edit / Delete).
"""

import customtkinter as ctk
from tkinter import messagebox
from config import C, VEHICLE_TYPES, FONT_LABEL
from ui.widgets import (
    _page_header, _section_label, _lf, _ef, _om, _btn,
    _status_lbl, _set_status, _treeview,
)
from db import (
    add_vehicle_db, get_vehicles_db,
    edit_vehicle_db, delete_vehicle_db,
)


class VehicleMixin:

    # ── Add Vehicle ───────────────────────────────────────────
    def show_add_vehicle(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add New Vehicle", "Register a motor vehicle")

            fields = [
                ("Plate Number *",    "plateNumber",   "e.g. ABC 1234"),
                ("Engine Number *",   "engineNumber",  ""),
                ("Chassis Number *",  "chassisNumber", ""),
                ("Make *",            "make",          "e.g. Toyota"),
                ("Model *",           "model",         "e.g. Vios"),
                ("Color *",           "color",         ""),
                ("Year *",            "year",          "YYYY"),
                ("Owner License No.*","licenseNumber", ""),
            ]
            entries = {}
            for i, (lbl, key, ph) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1, placeholder=ph)

            row = len(fields) + 1
            _lf(f, "Vehicle Type *", row, 0)
            type_var, _ = _om(f, VEHICLE_TYPES, row, 1)
            row += 1

            stat = _status_lbl(f, row, 0)
            row += 1

            def submit():
                try:
                    yr  = int(entries["year"].get().strip())
                    lic = int(entries["licenseNumber"].get().strip())
                except ValueError:
                    _set_status(stat,
                                "Year and License Number must be numeric.",
                                False)
                    return
                ok, msg = add_vehicle_db(
                    self.db, self.cur,
                    entries["plateNumber"].get().strip(),
                    entries["engineNumber"].get().strip(),
                    entries["chassisNumber"].get().strip(),
                    entries["make"].get().strip(),
                    entries["model"].get().strip(),
                    entries["color"].get().strip(),
                    type_var.get(), yr, lic,
                )
                _set_status(stat, msg, ok)
                if ok:
                    for e in entries.values():
                        e.delete(0, "end")

            _btn(f, "➕  Add Vehicle", submit, row, 0, colspan=2)

        self._switch(build)

    # ── View / Search ─────────────────────────────────────────
    def show_view_vehicles(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            f.grid_columnconfigure(3, weight=1)
            _page_header(f, "View / Search Vehicles",
                         "Filter and browse vehicle records")

            row = 1
            _section_label(f, "FILTER", row, colspan=4)
            row += 1

            _lf(f, "Plate Number", row, 0)
            e_plate = _ef(f, row, 1, 180)
            _lf(f, "License No.", row, 2)
            e_lic = _ef(f, row, 3, 180)
            row += 1

            _lf(f, "Make", row, 0)
            e_make = _ef(f, row, 1, 180)
            _lf(f, "Type", row, 2)
            type_var, _ = _om(f, ["All"] + VEHICLE_TYPES, row, 3, 200)
            row += 1

            stat_lbl = _status_lbl(f, row, 0, colspan=2)
            btn_row = row
            row += 1
            result = self._result_area(f, row, colspan=4)

            def search():
                for w in result.winfo_children():
                    w.destroy()
                crit = {}
                if e_plate.get().strip():
                    crit["plateNumber"] = e_plate.get().strip()
                if e_make.get().strip():
                    crit["make"] = e_make.get().strip()
                if type_var.get() != "All":
                    crit["type"] = type_var.get()
                if e_lic.get().strip():
                    try:
                        crit["licenseNumber"] = int(e_lic.get().strip())
                    except ValueError:
                        _set_status(stat_lbl,
                                    "License number must be numeric.", False)
                        return
                ok, rows = get_vehicles_db(self.db, self.cur, crit)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} record(s) found.", True)
                headers = ["Plate", "Engine", "Chassis", "Make", "Model",
                           "Color", "Type", "Year", "Lic No", "Owner"]
                _treeview(result, headers, rows)

            def view_all():
                for w in [e_plate, e_lic, e_make]:
                    w.delete(0, "end")
                type_var.set("All")
                search()

            _btn(f, "🔍  Search",   search,   btn_row, 0, style="primary")
            _btn(f, "📋  View All", view_all, btn_row, 1, style="secondary")

        self._switch(build)

    # ── Edit Vehicle ──────────────────────────────────────────
    def show_edit_vehicle(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Vehicle",
                         "Load a vehicle by plate number to modify its record")

            # Fetch plate list for dropdown
            plates = [""] + (
                [r[0] for r in
                 get_vehicles_db(self.db, self.cur)[1]]
                if get_vehicles_db(self.db, self.cur)[0] else []
            )

            _lf(f, "Plate Number:", 1, 0)
            plate_var, _ = _om(f, plates if plates else [""], 1, 1)
            stat = _status_lbl(f, 2, 0)

            inner = ctk.CTkFrame(f, fg_color=C["card"],
                                  corner_radius=8,
                                  border_width=1,
                                  border_color=C["card_border"])
            inner.grid(row=3, column=0, columnspan=2,
                       sticky="ew", padx=0, pady=8)
            inner.grid_columnconfigure(1, weight=1)
            entries  = {}
            vars_map = {}

            def load():
                for w in inner.winfo_children():
                    w.destroy()
                entries.clear()
                vars_map.clear()
                plate = plate_var.get().strip()
                if not plate:
                    _set_status(stat, "Select a plate number.", False)
                    return
                ok, rows = get_vehicles_db(self.db, self.cur,
                                           {"plateNumber": plate})
                if not ok or not rows:
                    _set_status(stat, "Vehicle not found.", False)
                    return
                r = rows[0]
                _set_status(stat,
                            f"Loaded: {r[3]} {r[4]} ({r[0]})", True)

                ef = [("Make",  "make",  r[3]),
                      ("Model", "model", r[4]),
                      ("Color", "color", r[5]),
                      ("Year",  "year",  str(r[7]))]
                for i, (lbl, key, val) in enumerate(ef):
                    _lf(inner, lbl + ":", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Type:", len(ef), 0)
                tv, _ = _om(inner, VEHICLE_TYPES, len(ef), 1)
                tv.set(r[6])
                vars_map["type"] = tv

                def save():
                    upd = {k: v.get().strip()
                           for k, v in entries.items()
                           if v.get().strip()}
                    upd["type"] = vars_map["type"].get()
                    if "year" in upd:
                        try:
                            upd["year"] = int(upd["year"])
                        except ValueError:
                            _set_status(stat,
                                        "Year must be numeric.", False)
                            return
                    ok2, msg = edit_vehicle_db(
                        self.db, self.cur, plate, upd)
                    _set_status(stat, msg, ok2)

                _btn(inner, "💾  Save Changes", save,
                     len(ef) + 1, 0, colspan=2)

            _btn(f, "⬇  Load Vehicle", load, 0, 1, style="secondary")

        self._switch(build)

    # ── Delete Vehicle ────────────────────────────────────────
    def show_delete_vehicle(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Delete Vehicle",
                         "Permanently remove a vehicle record")
            _lf(f, "Plate Number:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status_lbl(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm Delete",
                                           "Delete this vehicle?"):
                    return
                ok, msg = delete_vehicle_db(
                    self.db, self.cur, e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "🗑️  Delete Vehicle", delete, 2, 0,
                 colspan=2, style="danger")

        self._switch(build)
