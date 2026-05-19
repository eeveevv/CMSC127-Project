"""
ui/widgets.py
LTO IMS — Reusable widget factory helpers shared by all UI screens.
"""

import customtkinter as ctk
from tkinter import ttk
from config import C, FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_SMALL


# ── Cards & layout ────────────────────────────────────────────

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


# ── TTK Table ─────────────────────────────────────────────────

def _treeview(parent, headers, rows, col_widths=None):
    """Build a styled ttk.Treeview inside parent."""
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
    hdr = ctk.CTkFrame(parent, fg_color=C["sidebar_bg"], corner_radius=10)
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
