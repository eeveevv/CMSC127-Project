"""
ui/app.py
LTO IMS — LTOApp core class.

Fixes:
  • Sidebar highlight bug: nav_buttons now keyed by unique ID (label+section),
    not by label text — so "View / Search" under Drivers, Vehicles,
    Registrations, Violations no longer overwrite each other.
  • Delete screens: consistent row layout (entry row=1, btn row=2, stat row=3).
"""

import customtkinter as ctk
from tkinter import messagebox
import pymysql

from config import C, DB_CONFIG, FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_SMALL
from ui.widgets import _page_header, _treeview
from ui.drivers_ui       import DriverMixin
from ui.vehicles_ui      import VehicleMixin
from ui.registrations_ui import RegistrationMixin
from ui.violations_ui    import ViolationMixin
from ui.reports_ui       import ReportMixin


class LTOApp(
    DriverMixin,
    VehicleMixin,
    RegistrationMixin,
    ViolationMixin,
    ReportMixin,
    ctk.CTk,
):
    def __init__(self):
        super().__init__()
        self.title("LTO Information Management System")
        self.geometry("1380x860")
        self.minsize(1100, 720)
        self.configure(fg_color=C["bg"])

        self.db  = None
        self.cur = None
        self._connect()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()

        self.content = ctk.CTkFrame(
            self, fg_color=C["bg"], corner_radius=0)
        self.content.grid(row=0, column=1,
                          sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._current    = None
        self._active_btn = None
        self.show_dashboard()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── DB ────────────────────────────────────────────────────
    def _connect(self):
        try:
            self.db = pymysql.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                port=DB_CONFIG["port"],
                charset="utf8mb4",
                autocommit=False,
                cursorclass=pymysql.cursors.Cursor,
            )
            self.cur = self.db.cursor()
        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                f"Could not connect to MySQL:\n\n{e}"
            )

    def _on_close(self):
        try:
            if self.db:
                self.cur.close()
                self.db.close()
        except Exception:
            pass
        self.destroy()

    # ── Sidebar ───────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=220,
                          fg_color=C["sidebar_bg"], corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Branding
        logo_frame = ctk.CTkFrame(sb, fg_color="transparent")
        logo_frame.pack(fill="x", padx=14, pady=(20, 6))
        ctk.CTkLabel(logo_frame, text="🚗",
                     font=ctk.CTkFont(size=28)).pack(side="left", padx=(0, 8))
        title_v = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_v.pack(side="left")
        ctk.CTkLabel(title_v, text="LTO System",
                     font=ctk.CTkFont(
                         family="Segoe UI", size=16, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w")
        ctk.CTkLabel(title_v, text="CMSC 127 · 2S 2025-2026",
                     font=ctk.CTkFont(family="Segoe UI", size=9),
                     text_color=C["sidebar_muted"]).pack(anchor="w")

        # Gold separator
        ctk.CTkFrame(sb, height=2,
                     fg_color=C["sidebar_accent"]).pack(
            fill="x", padx=14, pady=(10, 6))

        scroll = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_button_color=C["sidebar_btn"],
            scrollbar_button_hover_color=C["sidebar_btn_hov"],
        )
        scroll.pack(fill="both", expand=True, padx=6, pady=4)

        # Each nav item: (unique_key, display_label, cmd_or_None, icon_or_None)
        # unique_key is used as the dict key — avoids collision on same label text
        sections = [
            # ── section headers (cmd=None) ──
            ("hdr_drivers",       "DRIVERS",        None,                          None),
            ("dashboard",         "  Dashboard",    self.show_dashboard,           "🏠"),
            ("add_driver",        "  Add Driver",   self.show_add_driver,          "➕"),
            ("view_drivers",      "  View / Search",self.show_view_drivers,        "🔍"),
            ("edit_driver",       "  Edit Driver",  self.show_edit_driver,         "✏️"),
            ("delete_driver",     "  Delete Driver",self.show_delete_driver,       "✖"),
            ("hdr_vehicles",      "VEHICLES",       None,                          None),
            ("add_vehicle",       "  Add Vehicle",  self.show_add_vehicle,         "➕"),
            ("view_vehicles",     "  View / Search",self.show_view_vehicles,       "🔍"),
            ("edit_vehicle",      "  Edit Vehicle", self.show_edit_vehicle,        "✏️"),
            ("delete_vehicle",    "  Delete Vehicle",self.show_delete_vehicle,     "✖"),
            ("hdr_regs",          "REGISTRATIONS",  None,                          None),
            ("add_reg",           "  Add Registration",     self.show_add_registration,    "➕"),
            ("view_regs",         "  View / Search",self.show_view_registrations,  "🔍"),
            ("edit_reg",          "  Edit Registration",    self.show_edit_registration,   "✏️"),
            ("delete_reg",        "  Delete Registration",  self.show_delete_registration, "✖"),
            ("hdr_violations",    "VIOLATIONS",     None,                          None),
            ("add_violation",     "  Add Violation",self.show_add_violation,       "➕"),
            ("view_violations",   "  View / Search",self.show_view_violations,     "🔍"),
            ("edit_violation",    "  Edit Violation",self.show_edit_violation,     "✏️"),
            ("delete_violation",  "  Delete Violation",self.show_delete_violation, "✖"),
            ("hdr_reports",       "REPORTS",        None,                          None),
            ("report1",           "  R1: All Drivers",  self.show_report1,         "📋"),
            ("report2",           "  R2: By Driver",    self.show_report2,         "🚘"),
            ("report3",           "  R3: Expired Reg.", self.show_report3,         "📅"),
            ("report4",           "  R4: Inactive",     self.show_report4,         "⚠️"),
            ("report5",           "  R5: Violations",   self.show_report5,         "🚨"),
            ("report6",           "  R6: Summary",      self.show_report6,         "📊"),
            ("report7",           "  R7: By Location",  self.show_report7,         "📍"),
        ]

        # _nav_buttons keyed by unique_key, not by display label
        self._nav_buttons = {}

        for unique_key, display_label, cmd, icon in sections:
            if cmd is None:
                # Section header
                ctk.CTkLabel(
                    scroll, text=display_label,
                    font=ctk.CTkFont(
                        family="Segoe UI", size=9, weight="bold"),
                    text_color=C["sidebar_accent"],
                    anchor="w",
                ).pack(fill="x", padx=8, pady=(12, 2))
            else:
                btn = ctk.CTkButton(
                    scroll,
                    text=f"{icon}  {display_label.strip()}",
                    command=lambda c=cmd, k=unique_key: self._nav(c, k),
                    anchor="w",
                    height=30,
                    corner_radius=6,
                    font=FONT_LABEL(),
                    fg_color="transparent",
                    hover_color=C["sidebar_btn_hov"],
                    text_color=C["sidebar_text"],
                )
                btn.pack(fill="x", padx=4, pady=1)
                self._nav_buttons[unique_key] = btn

    def _nav(self, cmd, unique_key):
        # Deselect previous button
        if self._active_btn and self._active_btn in \
                self._nav_buttons.values():
            self._active_btn.configure(
                fg_color="transparent",
                text_color=C["sidebar_text"],
            )
        btn = self._nav_buttons.get(unique_key)
        if btn:
            btn.configure(fg_color=C["sidebar_sel"],
                          text_color="#FFFFFF")
            self._active_btn = btn
        cmd()

    # ── View switcher ─────────────────────────────────────────
    def _switch(self, builder):
        if self._current:
            self._current.destroy()
        self._current = ctk.CTkScrollableFrame(
            self.content,
            fg_color=C["bg"],
            scrollbar_button_color=C["card_border"],
        )
        self._current.grid(row=0, column=0, sticky="nsew")
        self._current.grid_columnconfigure(0, weight=1)
        builder(self._current)

    # ── Result table frame ────────────────────────────────────
    def _result_area(self, parent, row, colspan=4):
        outer = ctk.CTkFrame(
            parent, fg_color=C["card"],
            corner_radius=8,
            border_width=1, border_color=C["card_border"],
        )
        outer.grid(row=row, column=0, columnspan=colspan,
                   sticky="nsew", padx=0, pady=(8, 4))
        parent.grid_rowconfigure(row, weight=1)
        inner = ctk.CTkFrame(outer, fg_color=C["card"])
        inner.pack(fill="both", expand=True, padx=6, pady=6)
        return inner

    # ── Dashboard ─────────────────────────────────────────────
    def show_dashboard(self):
        def build(f):
            f.grid_columnconfigure(0, weight=1)
            _page_header(f, "LTO Information Management System",
                         "Land Transportation Office · Philippines")

            if not self.db:
                ctk.CTkLabel(f, text="⚠  Not connected to database.",
                             text_color=C["error"],
                             font=FONT_SECTION()).grid(
                    row=1, column=0, pady=20)
                return

            try:
                counts = {}
                for tbl in ("driver", "vehicle", "registration", "violation"):
                    self.cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                    counts[tbl] = self.cur.fetchone()[0]
            except Exception as e:
                ctk.CTkLabel(f, text=f"Error: {e}",
                             text_color=C["error"]).grid(row=1, column=0)
                return

            tiles_frame = ctk.CTkFrame(f, fg_color="transparent")
            tiles_frame.grid(row=1, column=0, sticky="ew",
                             padx=0, pady=(0, 16))
            for i in range(4):
                tiles_frame.grid_columnconfigure(i, weight=1)

            tile_data = [
                ("Drivers",       counts["driver"],       C["tile_driver"],  "👤"),
                ("Vehicles",      counts["vehicle"],      C["tile_vehicle"], "🚘"),
                ("Registrations", counts["registration"], C["tile_reg"],     "📋"),
                ("Violations",    counts["violation"],    C["tile_vio"],     "🚨"),
            ]
            for i, (title, val, col, icon) in enumerate(tile_data):
                tile = ctk.CTkFrame(tiles_frame, fg_color=col,
                                    corner_radius=12)
                tile.grid(row=0, column=i, padx=8, pady=8, sticky="ew")
                tile.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(tile, text=icon,
                             font=ctk.CTkFont(size=28)).grid(
                    row=0, column=0, pady=(18, 4))
                ctk.CTkLabel(tile, text=str(val),
                             font=ctk.CTkFont(
                                 family="Segoe UI", size=40, weight="bold"),
                             text_color="#FFFFFF").grid(
                    row=1, column=0, pady=0)
                ctk.CTkLabel(tile, text=title,
                             font=ctk.CTkFont(family="Segoe UI", size=13),
                             text_color="#DBEAFE").grid(
                    row=2, column=0, pady=(0, 18))

            info_row = ctk.CTkFrame(f, fg_color="transparent")
            info_row.grid(row=2, column=0, sticky="ew", pady=(0, 12))
            info_row.grid_columnconfigure(0, weight=1)
            info_row.grid_columnconfigure(1, weight=1)

            def _info_card(parent, col, title, lines, icon):
                card = ctk.CTkFrame(
                    parent, fg_color=C["card"],
                    corner_radius=10,
                    border_width=1, border_color=C["card_border"],
                )
                card.grid(row=0, column=col, padx=8, sticky="nsew")
                card.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(card, text=f"{icon}  {title}",
                             font=FONT_SECTION(),
                             text_color=C["header_text"],
                             anchor="w").grid(
                    row=0, column=0, sticky="w", padx=16, pady=(14, 6))
                ctk.CTkFrame(card, height=1,
                             fg_color=C["card_border"]).grid(
                    row=1, column=0, sticky="ew", padx=12)
                for j, line in enumerate(lines):
                    ctk.CTkLabel(card, text=line,
                                 font=FONT_LABEL(),
                                 text_color=C["muted_text"],
                                 anchor="w").grid(
                        row=j + 2, column=0, sticky="w",
                        padx=16, pady=2)
                ctk.CTkFrame(card, height=10,
                             fg_color="transparent").grid(
                    row=j + 3, column=0)

            _info_card(info_row, 0, "System Overview",
                       ["Use the sidebar to navigate between modules.",
                        "All changes are saved to MySQL in real time.",
                        "Reports use SQL views defined in schema.sql."],
                       "ℹ️")

            try:
                self.cur.execute(
                    "SELECT violationId, type, violationDate "
                    "FROM violation ORDER BY violationDate DESC LIMIT 3"
                )
                recent = self.cur.fetchall()
                lines = [f"{r[0]}  –  {r[1]}  ({r[2]})"
                         for r in recent] \
                    if recent else ["No violations recorded yet."]
            except Exception:
                lines = ["Could not load recent violations."]

            _info_card(info_row, 1, "Recent Violations", lines, "🚨")

            ctk.CTkLabel(
                f,
                text="CMSC 127  ·  2nd Semester AY 2025–2026  ·  LTO IMS",
                font=FONT_SMALL(),
                text_color=C["muted_text"],
            ).grid(row=3, column=0, pady=(8, 20))

        self._switch(build)