"""
ui/registrations_ui.py
LTO IMS — Registration screen Mixin (Add / View / Edit / Delete).

Fixes:
  • show_edit_registration: Load button placed AFTER def load()
  • Consistent row layout: entry row=1, status row=2, inner row=3, load btn row=4
  • show_delete_registration: consistent row layout
"""

import customtkinter as ctk
from tkinter import messagebox
from config import C, REG_STATUSES
from ui.widgets import (
    _page_header, _lf, _ef, _om, _btn,
    _status_lbl, _set_status, _treeview,
)
from db import (
    add_registration_db, get_registrations_db,
    edit_registration_db, delete_registration_db,
)


class RegistrationMixin:

    # ── Add Registration ──────────────────────────────────────
    def show_add_registration(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add Registration",
                         "Record a new vehicle registration")

            fields = [
                ("Registration No. *", "registrationNumber", "e.g. REG-001"),
                ("Plate Number *",     "plateNumber",        ""),
                ("Registration Date *","registrationDate",   "YYYY-MM-DD"),
                ("Expiration Date *",  "expirationDate",     "YYYY-MM-DD"),
            ]
            entries = {}
            for i, (lbl, key, ph) in enumerate(fields, start=1):
                _lf(f, lbl, i, 0)
                entries[key] = _ef(f, i, 1, placeholder=ph)

            row = len(fields) + 1
            _lf(f, "Status *", row, 0)
            status_var, _ = _om(f, REG_STATUSES, row, 1)
            row += 1

            stat = _status_lbl(f, row, 0)
            row += 1

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

            _btn(f, "➕  Add Registration", submit, row, 0, colspan=2)

        self._switch(build)

    # ── View / Search ─────────────────────────────────────────
    def show_view_registrations(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "View / Search Registrations",
                         "Filter by plate number")

            _lf(f, "Plate Number (leave blank for all):", 1, 0)
            e_plate = _ef(f, 1, 1)
            stat_lbl = _status_lbl(f, 2, 0)

            result = self._result_area(f, 4, colspan=2)

            def search():
                for w in result.winfo_children():
                    w.destroy()
                plate = e_plate.get().strip() or None
                ok, rows = get_registrations_db(self.db, self.cur, plate)
                if not ok:
                    _set_status(stat_lbl, rows, False)
                    return
                _set_status(stat_lbl,
                            f"{len(rows)} record(s) found.", True)
                headers = ["Reg No", "Plate", "Status",
                           "Reg Date", "Exp Date", "Make", "Model"]
                _treeview(result, headers, rows)

            _btn(f, "🔍  Search", search, 3, 0, style="primary")
            _btn(f, "📋  View All",
                 lambda: (e_plate.delete(0, "end"), search()),
                 3, 1, style="secondary")

        self._switch(build)

    # ── Edit Registration ─────────────────────────────────────
    def show_edit_registration(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Registration",
                         "Type a registration number and click Load to edit")

            # row 1 — reg number entry
            _lf(f, "Registration Number:", 1, 0)
            e_reg = _ef(f, 1, 1, placeholder="e.g. REG-001")

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
                reg_no = e_reg.get().strip()
                if not reg_no:
                    _set_status(stat,
                                "Enter a registration number.", False)
                    return
                ok, rows = get_registrations_db(self.db, self.cur)
                rows = [r for r in rows
                        if r[0] == reg_no] if ok else []
                if not rows:
                    _set_status(stat, "Registration not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[0]}", True)

                ef = [
                    ("Registration Date (YYYY-MM-DD)",
                     "registrationDate", str(r[3])),
                    ("Expiration Date (YYYY-MM-DD)",
                     "expirationDate",   str(r[4])),
                ]
                for i, (lbl, key, val) in enumerate(ef):
                    _lf(inner, lbl + ":", i, 0)
                    e = _ef(inner, i, 1)
                    e.insert(0, val)
                    entries[key] = e

                _lf(inner, "Status:", len(ef), 0)
                sv, _ = _om(inner, REG_STATUSES, len(ef), 1)
                sv.set(r[2])
                vars_map["status"] = sv

                def save():
                    upd = {k: v.get().strip()
                           for k, v in entries.items()
                           if v.get().strip()}
                    upd["status"] = vars_map["status"].get()
                    ok2, msg = edit_registration_db(
                        self.db, self.cur, reg_no, upd)
                    _set_status(stat, msg, ok2)

                _btn(inner, "💾  Save Changes", save,
                     len(ef) + 1, 0, colspan=2)

            # Load button AFTER def load()
            _btn(f, "⬇  Load Registration", load, 4, 0, colspan=2,
                 style="secondary")

        self._switch(build)

    # ── Delete Registration ───────────────────────────────────
    def show_delete_registration(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Delete Registration",
                         "Permanently remove a registration record")

            _lf(f, "Registration Number:", 1, 0)
            e = _ef(f, 1, 1)
            stat = _status_lbl(f, 3, 0)

            def delete():
                if not messagebox.askyesno("Confirm Delete",
                                           "Delete this registration?"):
                    return
                ok, msg = delete_registration_db(
                    self.db, self.cur, e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "✖  Delete Registration", delete, 2, 0,
                 colspan=2, style="danger")

        self._switch(build)