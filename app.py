"""
app.py
LTO Information Management System
CMSC 127 | 2nd Semester AY 2025-2026

Visual theme: Philippine government deep navy + gold accent + crisp white cards.
Font stack: customtkinter default (scales cleanly on all platforms).
"""
#test, start na me guys -Paulo

import customtkinter as ctk
from tkinter import messagebox, ttk
import pymysql

from db_operations import (
    add_driver_db, get_drivers_db, edit_driver_db, delete_driver_db,
    upsert_driver_address_db,
    add_vehicle_db, get_vehicles_db, edit_vehicle_db, delete_vehicle_db,
    add_registration_db, get_registrations_db, edit_registration_db,
    delete_registration_db,
    add_violation_db, get_violations_db, edit_violation_db,
    delete_violation_db,
    report_all_drivers, report_vehicles_by_driver, report_expired_vehicles,
    report_inactive_drivers, report_violations_by_driver,
    report_violation_summary, report_vehicles_in_violations_by_location,
    get_all_plate_numbers, get_all_license_numbers,
)

# ── Appearance ────────────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ── DB Config ─────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "hellowrold",
    "database": "ltodata",
    "port": 3306,
}

# ── Domain constants ──────────────────────────────────────────
LICENSE_TYPES     = ["Professional", "Non-Professional", "Student Permit"]
LICENSE_STATUSES  = ["Valid", "Expired", "Suspended", "Revoked"]
SEX_OPTIONS       = ["Male", "Female"]
VIOLATION_STATUSES = ["Unpaid", "Paid", "Contested"]
REG_STATUSES      = ["Active", "Expired", "Suspended"]
VEHICLE_TYPES     = ["Private Car", "Motorcycle", "Public Utility Vehicle",
                     "Truck", "Bus"]

# ── Palette ───────────────────────────────────────────────────
C = {
    # Sidebar
    "sidebar_bg":      "#0A1A3E",   # deep navy
    "sidebar_btn":     "#122350",   # slightly lighter navy
    "sidebar_btn_hov": "#1B3370",
    "sidebar_sel":     "#1D4ED8",   # royal blue highlight
    "sidebar_text":    "#FFFFFF",
    "sidebar_muted":   "#8BA3CC",
    "sidebar_accent":  "#F5C518",   # LTO gold

    # Main area
    "bg":              "#F0F4FA",   # light blue-grey page
    "card":            "#FFFFFF",
    "card_border":     "#D1DCF0",
    "header_text":     "#0A1A3E",
    "body_text":       "#1E293B",
    "muted_text":      "#64748B",

    # Status
    "success":         "#16A34A",
    "error":           "#DC2626",
    "warn":            "#D97706",

    # Accent buttons
    "btn_primary":     "#1D4ED8",
    "btn_primary_hov": "#1E40AF",
    "btn_danger":      "#DC2626",
    "btn_danger_hov":  "#991B1B",
    "btn_secondary":   "#334155",
    "btn_secondary_hov": "#1E293B",

    # Tiles
    "tile_driver":     "#1D4ED8",
    "tile_vehicle":    "#059669",
    "tile_reg":        "#D97706",
    "tile_vio":        "#DC2626",

    # Table
    "tbl_header_bg":   "#0A1A3E",
    "tbl_header_fg":   "#FFFFFF",
    "tbl_row_even":    "#F8FAFF",
    "tbl_row_odd":     "#FFFFFF",
    "tbl_select":      "#DBEAFE",
    "tbl_border":      "#CBD5E1",
}

# CTkFont requires a root window to exist before instantiation.
# These are resolved lazily on first call — safe regardless of import order.
_font_cache: dict = {}

def _f(key: str) -> ctk.CTkFont:
    if key not in _font_cache:
        _font_cache[key] = {
            "title":   ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            "section": ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            "label":   ctk.CTkFont(family="Segoe UI", size=12),
            "small":   ctk.CTkFont(family="Segoe UI", size=11),
        }[key]
    return _font_cache[key]

# Convenience aliases — called as functions after root window exists
def FONT_TITLE():   return _f("title")
def FONT_SECTION(): return _f("section")
def FONT_LABEL():   return _f("label")
def FONT_SMALL():   return _f("small")
FONT_MONO = ("Courier New", 11)


# ══════════════════════════════════════════════════════════════
# WIDGET FACTORY HELPERS
# ══════════════════════════════════════════════════════════════

def _card(parent, **grid_kw):
    """Rounded white card frame."""
    f = ctk.CTkFrame(parent, fg_color=C["card"],
                     corner_radius=10,
                     border_width=1, border_color=C["card_border"])
    f.grid(**grid_kw)
    return f


def _section_label(parent, text, row, colspan=2):
    ctk.CTkLabel(
        parent, text=text, font=FONT_SECTION(),
        text_color=C["sidebar_accent"],
        fg_color=C["sidebar_bg"],
        corner_radius=4,
        padx=10, pady=3,
    ).grid(row=row, column=0, columnspan=colspan,
           sticky="w", padx=12, pady=(14, 4))


def _lf(parent, text, row, col, colspan=1):
    ctk.CTkLabel(
        parent, text=text,
        font=FONT_LABEL(), text_color=C["body_text"],
        anchor="w",
    ).grid(row=row, column=col, columnspan=colspan,
           sticky="w", padx=(12, 4), pady=4)


def _ef(parent, row, col, width=260, placeholder="", **kw):
    e = ctk.CTkEntry(
        parent, width=width,
        font=FONT_LABEL(),
        fg_color="#F8FAFF",
        border_color=C["card_border"],
        text_color=C["body_text"],
        placeholder_text=placeholder,
        **kw,
    )
    e.grid(row=row, column=col, padx=(4, 12), pady=4, sticky="ew")
    return e


def _om(parent, values, row, col, width=260):
    var = ctk.StringVar(value=values[0])
    m = ctk.CTkOptionMenu(
        parent, values=values, variable=var, width=width,
        font=FONT_LABEL(),
        fg_color="#F8FAFF",
        button_color=C["btn_primary"],
        button_hover_color=C["btn_primary_hov"],
        text_color=C["body_text"],
        dropdown_fg_color=C["card"],
        dropdown_text_color=C["body_text"],
        dropdown_hover_color=C["tbl_select"],
    )
    m.grid(row=row, column=col, padx=(4, 12), pady=4, sticky="ew")
    return var, m


def _btn(parent, text, cmd, row, col, colspan=1,
         style="primary", sticky="ew"):
    colors = {
        "primary":   (C["btn_primary"],   C["btn_primary_hov"]),
        "danger":    (C["btn_danger"],     C["btn_danger_hov"]),
        "secondary": (C["btn_secondary"],  C["btn_secondary_hov"]),
    }
    fg, hov = colors.get(style, colors["primary"])
    b = ctk.CTkButton(
        parent, text=text, command=cmd,
        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        fg_color=fg, hover_color=hov,
        text_color="#FFFFFF",
        corner_radius=6, height=34,
    )
    b.grid(row=row, column=col, columnspan=colspan,
           padx=(4, 12), pady=6, sticky=sticky)
    return b


def _status_lbl(parent, row, col, colspan=2):
    lbl = ctk.CTkLabel(parent, text="", font=FONT_LABEL())
    lbl.grid(row=row, column=col, columnspan=colspan,
             padx=12, pady=(2, 8), sticky="w")
    return lbl


def _set_status(lbl, msg, ok=True):
    lbl.configure(
        text=("✓  " if ok else "✗  ") + msg,
        text_color=C["success"] if ok else C["error"],
    )


def _divider(parent, row, colspan=2):
    ctk.CTkFrame(
        parent, height=1, fg_color=C["card_border"]
    ).grid(row=row, column=0, columnspan=colspan,
           sticky="ew", padx=12, pady=6)


# ── TTK Table (styled) ────────────────────────────────────────

def _treeview(parent, headers, rows, col_widths=None):
    """
    Build a styled ttk.Treeview inside parent.
    col_widths: list of pixel widths per column (auto if None).
    """
    # Scrollbars
    vsb = ttk.Scrollbar(parent, orient="vertical")
    hsb = ttk.Scrollbar(parent, orient="horizontal")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("LTO.Treeview",
                    background=C["tbl_row_odd"],
                    foreground=C["body_text"],
                    rowheight=26,
                    fieldbackground=C["tbl_row_odd"],
                    borderwidth=0,
                    font=("Segoe UI", 11))
    style.configure("LTO.Treeview.Heading",
                    background=C["tbl_header_bg"],
                    foreground=C["tbl_header_fg"],
                    font=("Segoe UI", 11, "bold"),
                    relief="flat",
                    padding=(6, 4))
    style.map("LTO.Treeview",
              background=[("selected", C["tbl_select"])],
              foreground=[("selected", C["body_text"])])
    style.map("LTO.Treeview.Heading",
              background=[("active", C["sidebar_sel"])])

    tv = ttk.Treeview(parent, columns=headers, show="headings",
                      style="LTO.Treeview",
                      yscrollcommand=vsb.set,
                      xscrollcommand=hsb.set)

    vsb.configure(command=tv.yview)
    hsb.configure(command=tv.xview)

    # Auto column widths
    if col_widths is None:
        col_widths = []
        for i, h in enumerate(headers):
            max_data = max(
                (len(str(r[i])) for r in rows if r[i] is not None),
                default=0
            )
            col_widths.append(max(len(str(h)) + 2, max_data + 2) * 9)

    for i, h in enumerate(headers):
        tv.heading(h, text=h)
        tv.column(h, width=col_widths[i], minwidth=60, anchor="w")

    # Alternating row tags
    tv.tag_configure("even", background=C["tbl_row_even"])
    tv.tag_configure("odd",  background=C["tbl_row_odd"])

    for idx, row in enumerate(rows):
        vals = tuple(str(v) if v is not None else "" for v in row)
        tv.insert("", "end", values=vals,
                  tags=("even" if idx % 2 == 0 else "odd",))

    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    return tv


# ── Page header ───────────────────────────────────────────────

def _page_header(parent, title, subtitle=""):
    hdr = ctk.CTkFrame(parent, fg_color=C["sidebar_bg"],
                       corner_radius=10)
    hdr.grid(row=0, column=0, columnspan=4,
             sticky="ew", padx=0, pady=(0, 16))
    hdr.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(hdr, text=title, font=FONT_TITLE(),
                 text_color="#FFFFFF",
                 anchor="w").grid(row=0, column=0,
                                  sticky="w", padx=18, pady=(12, 2))
    if subtitle:
        ctk.CTkLabel(hdr, text=subtitle, font=FONT_SMALL(),
                     text_color=C["sidebar_muted"],
                     anchor="w").grid(row=1, column=0,
                                      sticky="w", padx=18, pady=(0, 10))
    else:
        hdr.grid_rowconfigure(0, pad=8)
    return hdr


# ══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════

class LTOApp(ctk.CTk):
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

        self.content = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._current = None
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
        if self.db:
            self.cur.close()
            self.db.close()
        self.destroy()

    # ── Sidebar ───────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=220, fg_color=C["sidebar_bg"],
                          corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Logo / branding
        logo_frame = ctk.CTkFrame(sb, fg_color="transparent")
        logo_frame.pack(fill="x", padx=14, pady=(20, 6))

        ctk.CTkLabel(
            logo_frame, text="🚗",
            font=ctk.CTkFont(size=28),
        ).pack(side="left", padx=(0, 8))

        title_v = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_v.pack(side="left")
        ctk.CTkLabel(
            title_v, text="LTO System",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_v, text="CMSC 127 · 2S 2025-2026",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=C["sidebar_muted"],
        ).pack(anchor="w")

        # Gold separator
        ctk.CTkFrame(sb, height=2,
                     fg_color=C["sidebar_accent"]).pack(
            fill="x", padx=14, pady=(10, 6))

        # Nav items
        scroll = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_button_color=C["sidebar_btn"],
            scrollbar_button_hover_color=C["sidebar_btn_hov"],
        )
        scroll.pack(fill="both", expand=True, padx=6, pady=4)

        sections = [
            ("DRIVERS",        None),
            ("  Dashboard",    (self.show_dashboard,      "🏠")),
            ("  Add Driver",   (self.show_add_driver,     "➕")),
            ("  View / Search",(self.show_view_drivers,   "🔍")),
            ("  Edit Driver",  (self.show_edit_driver,    "✏️")),
            ("  Delete Driver",(self.show_delete_driver,  "🗑️")),
            ("VEHICLES",       None),
            ("  Add Vehicle",  (self.show_add_vehicle,    "➕")),
            ("  View / Search",(self.show_view_vehicles,  "🔍")),
            ("  Edit Vehicle", (self.show_edit_vehicle,   "✏️")),
            ("  Delete Vehicle",(self.show_delete_vehicle,"🗑️")),
            ("REGISTRATIONS",  None),
            ("  Add Reg.",     (self.show_add_registration,    "➕")),
            ("  View / Search",(self.show_view_registrations,  "🔍")),
            ("  Edit Reg.",    (self.show_edit_registration,   "✏️")),
            ("  Delete Reg.",  (self.show_delete_registration, "🗑️")),
            ("VIOLATIONS",     None),
            ("  Add Violation",(self.show_add_violation,    "➕")),
            ("  View / Search",(self.show_view_violations,  "🔍")),
            ("  Edit Violation",(self.show_edit_violation,  "✏️")),
            ("  Delete Violation",(self.show_delete_violation,"🗑️")),
            ("REPORTS",        None),
            ("  R1: All Drivers",   (self.show_report1, "📋")),
            ("  R2: By Driver",     (self.show_report2, "🚘")),
            ("  R3: Expired Reg.",  (self.show_report3, "📅")),
            ("  R4: Inactive",      (self.show_report4, "⚠️")),
            ("  R5: Violations",    (self.show_report5, "🚨")),
            ("  R6: Summary",       (self.show_report6, "📊")),
            ("  R7: By Location",   (self.show_report7, "📍")),
        ]

        self._nav_buttons = {}

        for label, action in sections:
            if action is None:
                # Section header
                ctk.CTkLabel(
                    scroll, text=label,
                    font=ctk.CTkFont(family="Segoe UI", size=9,
                                     weight="bold"),
                    text_color=C["sidebar_accent"],
                    anchor="w",
                ).pack(fill="x", padx=8, pady=(12, 2))
            else:
                cmd, icon = action
                btn = ctk.CTkButton(
                    scroll,
                    text=f"{icon}  {label.strip()}",
                    command=lambda c=cmd, b_label=label: self._nav(c, b_label),
                    anchor="w",
                    height=30,
                    corner_radius=6,
                    font=FONT_LABEL(),
                    fg_color="transparent",
                    hover_color=C["sidebar_btn_hov"],
                    text_color=C["sidebar_text"],
                )
                btn.pack(fill="x", padx=4, pady=1)
                self._nav_buttons[label] = btn

    def _nav(self, cmd, label):
        # Deselect previous
        if self._active_btn and self._active_btn in self._nav_buttons.values():
            self._active_btn.configure(
                fg_color="transparent",
                text_color=C["sidebar_text"],
            )
        btn = self._nav_buttons.get(label)
        if btn:
            btn.configure(
                fg_color=C["sidebar_sel"],
                text_color="#FFFFFF",
            )
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
        """Returns a frame ready for _treeview()."""
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

    # ══════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════
    def show_dashboard(self):
        def build(f):
            f.grid_columnconfigure(0, weight=1)

            _page_header(f, "LTO Information Management System",
                         "Land Transportation Office · Philippines")

            if not (self.db):
                ctk.CTkLabel(f, text="⚠  Not connected to database.",
                             text_color=C["error"],
                             font=FONT_SECTION()).grid(
                    row=1, column=0, pady=20)
                return

            # Summary tiles
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
                tile = ctk.CTkFrame(
                    tiles_frame, fg_color=col,
                    corner_radius=12,
                )
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
                             font=ctk.CTkFont(
                                 family="Segoe UI", size=13),
                             text_color="#DBEAFE").grid(
                    row=2, column=0, pady=(0, 18))

            # Quick-info cards
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

                ctk.CTkLabel(card,
                             text=f"{icon}  {title}",
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
                             fg_color="transparent").grid(row=j+3, column=0)

            _info_card(info_row, 0, "System Overview",
                       ["Use the sidebar to navigate between modules.",
                        "All changes are saved to MySQL in real time.",
                        "Reports use SQL views defined in schema.sql."],
                       "ℹ️")

            # Fetch latest 3 violations
            try:
                self.cur.execute(
                    "SELECT violationId, type, violationDate "
                    "FROM violation ORDER BY violationDate DESC LIMIT 3"
                )
                recent = self.cur.fetchall()
                lines = [f"{r[0]}  –  {r[1]}  ({r[2]})" for r in recent] \
                    if recent else ["No violations recorded yet."]
            except Exception:
                lines = ["Could not load recent violations."]

            _info_card(info_row, 1, "Recent Violations", lines, "🚨")

            ctk.CTkLabel(f,
                         text="CMSC 127  ·  2nd Semester AY 2025–2026  ·  LTO IMS",
                         font=FONT_SMALL(),
                         text_color=C["muted_text"]).grid(
                row=3, column=0, pady=(8, 20))

        self._switch(build)

    # ══════════════════════════════════════════
    # ── DRIVER SCREENS ──────────────────────
    # ══════════════════════════════════════════

    def show_add_driver(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add New Driver", "Create a driver licence record")

            row = 1
            _section_label(f, "LICENCE INFORMATION", row)
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
                                self.db, self.cur, lic_num, addr, city, reg)
                        except ValueError:
                            pass
                    for w in [e_lic, e_name, e_dob, e_issued, e_expiry,
                              e_addr, e_city, e_region]:
                        w.delete(0, "end")

            _btn(f, "➕  Add Driver", submit, row, 0, colspan=2)

        self._switch(build)

    # ─────────────────────────────────────────
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
            row += 1

            def search():
                for w in result.winfo_children():
                    w.destroy()
                crit = {}
                if e_lic.get().strip():
                    try:
                        crit["licenseNumber"] = int(e_lic.get().strip())
                    except ValueError:
                        _set_status(stat_lbl, "License number must be numeric.", False)
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
                _set_status(stat_lbl, f"{len(rows)} record(s) found.", True)
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

            _btn(f, "🔍  Search", search, btn_row, 0, style="primary")
            _btn(f, "📋  View All", view_all, btn_row, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
    def show_edit_driver(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Driver",
                         "Load a driver by licence number to modify their record")

            row = 1
            _lf(f, "License Number:", row, 0)
            e_lic = _ef(f, row, 1)
            stat  = _status_lbl(f, row + 1, 0)
            row += 2

            inner = ctk.CTkFrame(f, fg_color=C["card"],
                                 corner_radius=8,
                                 border_width=1, border_color=C["card_border"])
            inner.grid(row=row, column=0, columnspan=2,
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
                    _set_status(stat, "License number must be numeric.", False)
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
                    ("Full Name",        "fullName",               r[1]),
                    ("Issuance Date",    "licenseIssuanceDate",    str(r[4])),
                    ("Expiration Date",  "licenseExpirationDate",  str(r[5])),
                    ("Date of Birth",    "dateOfBirth",            str(r[6])),
                    ("Address",          "_addr",                  str(r[9]  or "")),
                    ("City",             "_city",                  str(r[10] or "")),
                    ("Region",           "_region",                str(r[11] or "")),
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

            _btn(f, "⬇  Load Driver", load, 0, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
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
                    _set_status(stat, "License number must be numeric.", False)
                    return
                ok, msg = delete_driver_db(self.db, self.cur, lic)
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "🗑️  Delete Driver", delete, 2, 0, colspan=2,
                 style="danger")

        self._switch(build)

    # ══════════════════════════════════════════
    # ── VEHICLE SCREENS ──────────────────────
    # ══════════════════════════════════════════

    def show_add_vehicle(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add New Vehicle", "Register a motor vehicle")

            fields = [
                ("Plate Number *",   "plateNumber",   "e.g. ABC 1234"),
                ("Engine Number *",  "engineNumber",  ""),
                ("Chassis Number *", "chassisNumber", ""),
                ("Make *",           "make",          "e.g. Toyota"),
                ("Model *",          "model",         "e.g. Vios"),
                ("Color *",          "color",         ""),
                ("Year *",           "year",          "YYYY"),
                ("Owner License No.*","licenseNumber",""),
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

    # ─────────────────────────────────────────
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
                _set_status(stat_lbl, f"{len(rows)} record(s) found.", True)
                headers = ["Plate", "Engine", "Chassis", "Make", "Model",
                           "Color", "Type", "Year", "Lic No", "Owner"]
                _treeview(result, headers, rows)

            def view_all():
                for w in [e_plate, e_lic, e_make]:
                    w.delete(0, "end")
                type_var.set("All")
                search()

            _btn(f, "🔍  Search", search, btn_row, 0, style="primary")
            _btn(f, "📋  View All", view_all, btn_row, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
    def show_edit_vehicle(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Vehicle",
                         "Load a vehicle by plate number to modify its record")

            row = 1
            _lf(f, "Plate Number:", 1, 0)
            plate_var, plate_menu = _om(f, plates, 1, 1)
            stat = _status_lbl(f, 2, 0)
            row += 2

            inner = ctk.CTkFrame(f, fg_color=C["card"],
                                corner_radius=8,
                                border_width=1, border_color=C["card_border"])
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
                _set_status(stat, f"Loaded: {r[3]} {r[4]} ({r[0]})", True)

                ef = [("Make","make",r[3]),("Model","model",r[4]),
                    ("Color","color",r[5]),("Year","year",str(r[7]))]
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
                        for k, v in entries.items() if v.get().strip()}
                    upd["type"] = vars_map["type"].get()
                    if "year" in upd:
                        try:
                            upd["year"] = int(upd["year"])
                        except ValueError:
                            _set_status(stat, "Year must be numeric.", False)
                            return
                    ok2, msg = edit_vehicle_db(self.db, self.cur, plate, upd)
                    _set_status(stat, msg, ok2)

                _btn(inner, "💾  Save Changes", save, len(ef) + 1, 0,
                    colspan=2)

            _btn(f, "⬇  Load Vehicle", load, 0, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
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
                ok, msg = delete_vehicle_db(self.db, self.cur,
                                            e.get().strip())
                _set_status(stat, msg, ok)
                if ok:
                    e.delete(0, "end")

            _btn(f, "🗑️  Delete Vehicle", delete, 2, 0,
                 colspan=2, style="danger")

        self._switch(build)

    # ══════════════════════════════════════════
    # ── REGISTRATION SCREENS ─────────────────
    # ══════════════════════════════════════════

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

    # ─────────────────────────────────────────
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

    # ─────────────────────────────────────────
    def show_edit_registration(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Registration",
                         "Load a registration by number to modify it")

            row=1
            _lf(f, "Registration Number:", 1, 0)
            e_reg = _ef(f, 1, 1)
            stat = _status_lbl(f, 2, 0)
            row += 2

            inner = ctk.CTkFrame(f, fg_color=C["card"],
                                 corner_radius=8,
                                 border_width=1, border_color=C["card_border"])
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
                    _set_status(stat, "Enter a registration number.", False)
                    return
                ok, rows = get_registrations_db(self.db, self.cur)
                rows = [r for r in rows if r[0] == reg_no] if ok else []
                if not rows:
                    _set_status(stat, "Registration not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[0]}", True)

                ef = [("Registration Date (YYYY-MM-DD)",
                        "registrationDate", str(r[3])),
                      ("Expiration Date (YYYY-MM-DD)",
                        "expirationDate",   str(r[4]))]
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
                           for k, v in entries.items() if v.get().strip()}
                    upd["status"] = vars_map["status"].get()
                    ok2, msg = edit_registration_db(
                        self.db, self.cur, reg_no, upd)
                    _set_status(stat, msg, ok2)

                _btn(inner, "💾  Save Changes", save,
                     len(ef) + 1, 0, colspan=2)

            _btn(f, "⬇  Load Registration", load, 0, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
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

            _btn(f, "🗑️  Delete Registration", delete,
                 2, 0, colspan=2, style="danger")

        self._switch(build)

    # ══════════════════════════════════════════
    # ── VIOLATION SCREENS ────────────────────
    # ══════════════════════════════════════════

    def show_add_violation(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Add Violation",
                         "Record a new traffic violation")

            fields = [
                ("Violation ID *",         "violationId",        "e.g. VIO-001"),
                ("License Number *",       "licenseNumber",      ""),
                ("Plate Number *",         "plateNumber",        ""),
                ("Violation Type *",       "type",               "e.g. Overspeeding"),
                ("Location *",             "location",           "Street, City"),
                ("Violation Date *",       "violationDate",      "YYYY-MM-DD"),
                ("Fine Amount (PHP) *",    "fineAmount",         "e.g. 2000.00"),
                ("Apprehending Officer",   "apprehendingOfficer","Optional"),
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
                    _set_status(
                        stat,
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

    # ─────────────────────────────────────────
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

            _btn(f, "🔍  Search", search, btn_row, 0, style="primary")
            _btn(f, "📋  View All", view_all, btn_row, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
    def show_edit_violation(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Edit Violation",
                         "Load a violation by ID to modify it")

            row = 1
            _lf(f, "Violation ID:", 1, 0)
            e_vid = _ef(f, 1, 1)
            stat = _status_lbl(f, 2, 0)
            row += 2

            inner = ctk.CTkFrame(f, fg_color=C["card"],
                                 corner_radius=8,
                                 border_width=1, border_color=C["card_border"])
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
                rows = [r for r in rows if r[0] == vid] if ok else []
                if not rows:
                    _set_status(stat, "Violation not found.", False)
                    return
                r = rows[0]
                _set_status(stat, f"Loaded: {r[0]}", True)

                ef = [
                    ("Type",       "type",               str(r[5])),
                    ("Location",   "location",           str(r[6])),
                    ("Fine Amount","fineAmount",          str(r[8])),
                    ("Officer",    "apprehendingOfficer", str(r[9] or "")),
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
                           for k, v in entries.items() if v.get().strip()}
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

            _btn(f, "⬇  Load Violation", load, 0, 1, style="secondary")

        self._switch(build)

    # ─────────────────────────────────────────
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

            _btn(f, "🗑️  Delete Violation", delete,
                 2, 0, colspan=2, style="danger")

        self._switch(build)

    # ══════════════════════════════════════════
    # ── REPORT SCREENS ───────────────────────
    # ══════════════════════════════════════════

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

    # ─────────────────────────────────────────
    def show_report2(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Report 2 — Vehicles Owned by a Driver",
                         "Enter a licence number to list all registered vehicles")

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
                ok, rows = report_vehicles_by_driver(self.db, self.cur, lic)
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

    # ─────────────────────────────────────────
    def show_report3(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Report 3 — Vehicles with Expired Registrations",
                         "Leave date blank to use today's date")

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

    # ─────────────────────────────────────────
    def show_report4(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(
                f,
                "Report 4 — Inactive Drivers",
                "Drivers with Expired, Suspended, or Revoked licences"
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

    # ─────────────────────────────────────────
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

    # ─────────────────────────────────────────
    def show_report6(self):
        def build(f):
            f.grid_columnconfigure(1, weight=1)
            _page_header(f, "Report 6 — Violation Count per Type per Year",
                         "Total violations grouped by type for a given year")

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

    # ─────────────────────────────────────────
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


# ══════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = LTOApp()
    app.mainloop()