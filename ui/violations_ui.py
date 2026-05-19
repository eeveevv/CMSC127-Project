"""
ui/violations_ui.py
LTO IMS — Violation screen Mixin (Add / View / Edit / Delete).

Fixes:
  • show_edit_violation: Load button placed AFTER def load()
  • Consistent row layout: entry row=1, status row=2, inner row=3, load btn row=4
  • show_delete_violation: consistent row layout
"""

import customtkinter as ctk
from tkinter import messagebox
from config import C, VIOLATION_STATUSES
from ui.widgets import (
    _page_header, _section_label, _lf, _ef, _om, _btn,
    _status_lbl, _set_status, _treeview,
)
from db import (
    add_violation_db, get_violations_db,
    edit_violation_db, delete_violation_db,
)


class ViolationMixin:

    # ── Add Violation ─────────────────────────────────────────
    def show_add_violation(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add Violation",
                         "Record a new traffic violation")

            fields = [
                ("Violation ID *",       "violationId",        "e.g. VIO-001"),
                ("License Number *",     "licenseNumber",      ""),
                ("Plate Number *",       "plateNumber",        ""),
                ("Violation Type *",     "type",               "e.g. Overspeeding"),
                ("Location *",           "location",           "Street, City"),
                ("Violation Date *",     "violationDate",      "YYYY-MM-DD"),
                ("Fine Amount (PHP) *",  "fineAmount",         "e.g. 2000.00"),
                ("Apprehending Officer", "apprehendingOfficer","Optional"),
            ]
            entries = {}
            for i, (lbl, key, ph) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1, placeholder=ph)

            row = len(fields) + 1
            _lf(f, "Status *", row, 0)
            status_var, _ = _om(f, VIOLATION_STATUSES, row, 1)
            row += 1

            stat = _status_lbl(f, row, 0)
            row += 1

            def submit():
                try:
                    lic  = int(entries["licenseNumber"].get().strip())
                    fine = float(entries["fineAmount"].get().strip())
                except ValueError:
                    _set_status(stat,
                                "License number must be integer; "
                                "fine must be a number.", False)
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
                    entries["apprehendingOfficer"].get().strip() or None,
                )
                _set_status(stat, msg, ok)
                if ok:
                    for e in entries.values():
                        e.delete(0, "end")

            _btn(f, "➕  Add Violation", submit, row, 0, colspan=2)

        self._switch(build)

    # ── View / Search ─────────────────────────────────────────
    def show_view_violations(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            f.grid_columnconfigure(3, weight=1)
            _page_header(f, "View / Search Violations",
                         "Filter and browse violation records")

            row = 1
            _section_label(f, "FILTER", row, colspan=4)
            row += 1

            _lf(f, "License No.", row, 0)
            e_lic = _ef(f, row, 1, 180)
            _lf(f, "Plate No.", row, 2)
            e_plate = _ef(f, row, 3, 180)
            row += 1

            _lf(f, "Status", row, 0)
            stat_var, _ = _om(f, ["All"] + VIOLATION_STATUSES, row, 1, 200)
            _lf(f, "Date From", row, 2)
            e_from = _ef(f, row, 3, 180, placeholder="YYYY-MM-DD")
            row += 1

            _lf(f, "Date To", row, 2)
            e_to = _ef(f, row, 3, 180, placeholder="YYYY-MM-DD")

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
                if e_plate.get().strip():
                    crit["plateNumber"] = e_plate.get().strip()
                if stat_var.get() != "All":
                    crit["status"] = stat_var.get()
                if e_from.get().strip():
                    crit["date_from"] = e_from.get().strip()
                if e_to.get().strip():
                    crit["date_to"] = e_to.get().strip()

                ok, rows = get_violations_db(self.db, self.cur, crit)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} record(s) found.", True)
                headers = ["Vio ID", "Lic No", "Name", "Plate",
                           "Status", "Type", "Location",
                           "Date", "Fine (PHP)", "Officer"]
                _treeview(result, headers, rows)

            def view_all():
                for w in [e_lic, e_plate, e_from, e_to]:
                    w.delete(0, "end")
                stat_var.set("All")
                search()

            _btn(f, "🔍  Search",   search,   btn_row, 0, style="primary")
            _btn(f, "📋  View All", view_all, btn_row, 1, style="secondary")

        self._switch(build)

    # ── Edit Violation ────────────────────────────────────────
    def show_edit_violation(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Violation",
                         "Type a violation ID and click Load to edit")

            # row 1 — violation ID entry
            _lf(f, "Violation ID:", 1, 0)
            e_vid = _ef(f, 1, 1, placeholder="e.g. VIO-001")

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
                vid = e_vid.get().strip()
                if not vid:
                    _set_status(stat, "Enter a violation ID.", False)
                    return
                ok, rows = get_violations_db(self.db, self.cur, {})
                rows = [r for r in rows
                        if r[0] == vid] if ok else []
                if not rows:
                    _set_status(stat, "Violation not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[0]}", True)

                ef = [
                    ("Type",        "type",               str(r[5])),
                    ("Location",    "location",           str(r[6])),
                    ("Fine Amount", "fineAmount",         str(r[8])),
                    ("Officer",     "apprehendingOfficer",str(r[9] or "")),
                ]
                for i, (lbl, key, val) in enumerate(ef):
                    _lf(inner, lbl + ":", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Status:", len(ef), 0)
                sv, _ = _om(inner, VIOLATION_STATUSES, len(ef), 1)
                sv.set(r[4])
                vars_map["status"] = sv

                def save():
                    upd = {k: v.get().strip()
                           for k, v in entries.items()
                           if v.get().strip()}
                    upd["status"] = vars_map["status"].get()
                    if "fineAmount" in upd:
                        try:
                            upd["fineAmount"] = float(upd["fineAmount"])
                        except ValueError:
                            _set_status(stat,
                                        "Fine amount must be numeric.", False)
                            return
                    ok2, msg = edit_violation_db(
                        self.db, self.cur, vid, upd)
                    _set_status(stat, msg, ok2)

                _btn(inner, "💾  Save Changes", save,
                     len(ef) + 1, 0, colspan=2)

            # Load button AFTER def load()
            _btn(f, "⬇  Load Violation", load, 4, 0, colspan=2,
                 style="secondary")

        self._switch(build)

    # ── Delete Violation ──────────────────────────────────────
    def show_delete_violation(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Delete Violation",
                         "Permanently remove a violation record")

            _lf(f, "Violation ID:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status_lbl(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm Delete",
                                           "Delete this violation?"):
                    return
                ok, msg = delete_violation_db(
                    self.db, self.cur, e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "✖  Delete Violation", delete, 2, 0,
                 colspan=2, style="danger")

        self._switch(build)