"""
ui/drivers_ui.py
LTO IMS — Driver screen Mixin (Add / View / Edit / Delete).

Fixes:
  • show_edit_driver: Load button moved to row=0,col=1 which is fine since
    it's in a separate call before the inner frame — but kept consistent.
  • show_delete_driver: row layout row=1 entry, row=2 btn, row=3 status.
"""

import customtkinter as ctk
from tkinter import messagebox
from config import (C, LICENSE_TYPES, LICENSE_STATUSES, SEX_OPTIONS,
                    FONT_LABEL, FONT_SECTION)
from ui.widgets import (
    _page_header, _section_label, _lf, _ef, _om, _btn,
    _status_lbl, _set_status, _divider, _treeview,
)
from db import (
    add_driver_db, get_drivers_db, edit_driver_db,
    delete_driver_db, upsert_driver_address_db,
)


class DriverMixin:

    # ── Add Driver ────────────────────────────────────────────
    def show_add_driver(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add New Driver",
                         "Create a driver license record")

            row = 1
            _section_label(f, "LICENSE INFORMATION", row)
            row += 1

            _lf(f, "License Number *", row, 0)
            e_lic = _ef(f, row, 1, placeholder="e.g. 1000001")
            row += 1

            _lf(f, "Full Name *", row, 0)
            e_name = _ef(f, row, 1, placeholder="Last, First M.")
            row += 1

            _lf(f, "Date of Birth *", row, 0)
            e_dob = _ef(f, row, 1, placeholder="YYYY-MM-DD")
            row += 1

            _lf(f, "Sex *", row, 0)
            sex_var, _ = _om(f, SEX_OPTIONS, row, 1)
            row += 1

            _lf(f, "License Type *", row, 0)
            type_var, _ = _om(f, LICENSE_TYPES, row, 1)
            row += 1

            _lf(f, "License Status *", row, 0)
            status_var, _ = _om(f, LICENSE_STATUSES, row, 1)
            row += 1

            _lf(f, "Issuance Date *", row, 0)
            e_issued = _ef(f, row, 1, placeholder="YYYY-MM-DD")
            row += 1

            _lf(f, "Expiration Date *", row, 0)
            e_expiry = _ef(f, row, 1, placeholder="YYYY-MM-DD")
            row += 1

            _divider(f, row)
            row += 1

            _section_label(f, "ADDRESS  (optional)", row)
            row += 1

            _lf(f, "Street / Barangay", row, 0)
            e_addr = _ef(f, row, 1)
            row += 1

            _lf(f, "City", row, 0)
            e_city = _ef(f, row, 1)
            row += 1

            _lf(f, "Region", row, 0)
            e_region = _ef(f, row, 1)
            row += 1

            stat = _status_lbl(f, row, 0)
            row += 1

            def submit():
                ok, msg = add_driver_db(
                    self.db, self.cur,
                    e_lic.get().strip(), e_name.get().strip(),
                    status_var.get(), type_var.get(),
                    e_issued.get().strip(), e_expiry.get().strip(),
                    e_dob.get().strip(), sex_var.get(),
                )
                _set_status(stat, msg, ok)
                if ok:
                    addr = e_addr.get().strip()
                    city = e_city.get().strip()
                    reg  = e_region.get().strip()
                    if addr and city and reg:
                        try:
                            lic_num = int(e_lic.get().strip())
                            upsert_driver_address_db(
                                self.db, self.cur,
                                lic_num, addr, city, reg)
                        except ValueError:
                            pass
                    for w in [e_lic, e_name, e_dob, e_issued, e_expiry,
                              e_addr, e_city, e_region]:
                        w.delete(0, "end")

            _btn(f, "➕  Add Driver", submit, row, 0, colspan=2)

        self._switch(build)

    # ── View / Search ─────────────────────────────────────────
    def show_view_drivers(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            f.grid_columnconfigure(3, weight=1)
            _page_header(f, "View / Search Drivers",
                         "Filter and browse driver records")

            row = 1
            _section_label(f, "FILTER", row, colspan=4)
            row += 1

            _lf(f, "License No.", row, 0)
            e_lic = _ef(f, row, 1, 180)
            _lf(f, "Name", row, 2)
            e_name = _ef(f, row, 3, 200)
            row += 1

            _lf(f, "Type", row, 0)
            type_var, _ = _om(f, ["All"] + LICENSE_TYPES, row, 1, 200)
            _lf(f, "Status", row, 2)
            stat_var, _ = _om(f, ["All"] + LICENSE_STATUSES, row, 3, 200)
            row += 1

            _lf(f, "Sex", row, 0)
            sex_var, _ = _om(f, ["All"] + SEX_OPTIONS, row, 1, 200)
            _lf(f, "Age Min", row, 2)
            e_amin = _ef(f, row, 3, 80)
            row += 1

            _lf(f, "Age Max", row, 2)
            e_amax = _ef(f, row, 3, 80)

            stat_lbl = _status_lbl(f, row, 0, colspan=2)
            row += 1

            btn_row = row
            row += 1

            result = self._result_area(f, row, colspan=4)

            def search():
                for w in result.winfo_children():
                    w.destroy()
                crit = {}
                if e_lic.get().strip():
                    try:
                        crit["licenseNumber"] = int(e_lic.get().strip())
                    except ValueError:
                        _set_status(stat_lbl,
                                    "License number must be numeric.", False)
                        return
                if e_name.get().strip():
                    crit["fullName"] = e_name.get().strip()
                if type_var.get() != "All":
                    crit["licenseType"] = type_var.get()
                if stat_var.get() != "All":
                    crit["licenseStatus"] = stat_var.get()
                if sex_var.get() != "All":
                    crit["sex"] = sex_var.get()
                if e_amin.get().strip():
                    try:
                        crit["age_min"] = int(e_amin.get().strip())
                    except ValueError:
                        pass
                if e_amax.get().strip():
                    try:
                        crit["age_max"] = int(e_amax.get().strip())
                    except ValueError:
                        pass

                ok, rows = get_drivers_db(self.db, self.cur, crit)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} record(s) found.", True)
                headers = ["Lic No", "Full Name", "Status", "Type",
                           "Issued", "Expires", "DOB", "Age", "Sex",
                           "Address", "City", "Region"]
                _treeview(result, headers, rows)

            def view_all():
                for w in [e_lic, e_name, e_amin, e_amax]:
                    w.delete(0, "end")
                type_var.set("All")
                stat_var.set("All")
                sex_var.set("All")
                search()

            _btn(f, "🔍  Search",   search,   btn_row, 0, style="primary")
            _btn(f, "📋  View All", view_all, btn_row, 1, style="secondary")

        self._switch(build)

    # ── Edit Driver ───────────────────────────────────────────
    def show_edit_driver(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Driver",
                         "Load a driver by license number to modify their record")

            # row 1 — license entry
            _lf(f, "License Number:", 1, 0)
            e_lic = _ef(f, 1, 1, placeholder="e.g. 1000001")

            # row 2 — status label
            stat = _status_lbl(f, 2, 0)

            # row 3 — inner edit card
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
                try:
                    lic = int(e_lic.get().strip())
                except ValueError:
                    _set_status(stat,
                                "License number must be numeric.", False)
                    return
                ok, rows = get_drivers_db(self.db, self.cur,
                                          {"licenseNumber": lic})
                if not ok or not rows:
                    _set_status(stat, "Driver not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[1]}", True)

                irow = 0
                edit_fields = [
                    ("Full Name",       "fullName",              r[1]),
                    ("Issuance Date",   "licenseIssuanceDate",   str(r[4])),
                    ("Expiration Date", "licenseExpirationDate", str(r[5])),
                    ("Date of Birth",   "dateOfBirth",           str(r[6])),
                    ("Address",         "_addr",                 str(r[9]  or "")),
                    ("City",            "_city",                 str(r[10] or "")),
                    ("Region",          "_region",               str(r[11] or "")),
                ]
                for lbl, key, val in edit_fields:
                    _lf(inner, lbl + ":", irow, 0)
                    e = _ef(inner, irow, 1)
                    e.insert(0, val)
                    entries[key] = e
                    irow += 1

                _lf(inner, "Sex:", irow, 0)
                sv, _ = _om(inner, SEX_OPTIONS, irow, 1)
                sv.set(r[8])
                vars_map["sex"] = sv
                irow += 1

                _lf(inner, "License Type:", irow, 0)
                tv, _ = _om(inner, LICENSE_TYPES, irow, 1)
                tv.set(r[3])
                vars_map["licenseType"] = tv
                irow += 1

                _lf(inner, "License Status:", irow, 0)
                stv, _ = _om(inner, LICENSE_STATUSES, irow, 1)
                stv.set(r[2])
                vars_map["licenseStatus"] = stv
                irow += 1

                def save():
                    upd = {}
                    for key, widget in entries.items():
                        if not key.startswith("_"):
                            val2 = widget.get().strip()
                            if val2:
                                upd[key] = val2
                    upd["sex"]           = vars_map["sex"].get()
                    upd["licenseType"]   = vars_map["licenseType"].get()
                    upd["licenseStatus"] = vars_map["licenseStatus"].get()

                    ok2, msg = edit_driver_db(self.db, self.cur, lic, upd)
                    _set_status(stat, msg, ok2)

                    addr   = entries["_addr"].get().strip()
                    city   = entries["_city"].get().strip()
                    region = entries["_region"].get().strip()
                    if addr and city and region:
                        upsert_driver_address_db(
                            self.db, self.cur, lic, addr, city, region)

                _btn(inner, "💾  Save Changes", save, irow, 0, colspan=2)

            # Load button AFTER def load()
            _btn(f, "⬇  Load Driver", load, 4, 0, colspan=2,
                 style="secondary")

        self._switch(build)

    # ── Delete Driver ─────────────────────────────────────────
    def show_delete_driver(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Delete Driver",
                         "Permanently remove a driver record")

            _lf(f, "License Number:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status_lbl(f, 3, 0)

            def delete():
                if not messagebox.askyesno(
                    "Confirm Delete",
                    "Delete this driver?\n"
                    "This cannot be undone. Linked vehicles/violations "
                    "will block deletion."
                ):
                    return
                try:
                    lic = int(e.get().strip())
                except ValueError:
                    _set_status(stat,
                                "License number must be numeric.", False)
                    return
                ok, msg = delete_driver_db(self.db, self.cur, lic)
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "✖  Delete Driver", delete, 2, 0,
                 colspan=2, style="danger")

        self._switch(build)