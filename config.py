"""
config.py
LTO Information Management System
CMSC 127 | 2nd Semester AY 2025-2026

Central configuration: DB credentials, domain constants, colour palette,
and lazy-loaded font helpers.
"""

import customtkinter as ctk

# ── DB Config ─────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "hellowrold",
    "database": "ltodata",
    "port":     3306,
}

# ── Domain constants ──────────────────────────────────────────
LICENSE_TYPES      = ["Professional", "Non-Professional", "Student Permit"]
LICENSE_STATUSES   = ["Valid", "Expired", "Suspended", "Revoked"]
SEX_OPTIONS        = ["Male", "Female"]
VIOLATION_STATUSES = ["Unpaid", "Paid", "Contested"]
REG_STATUSES       = ["Active", "Expired", "Suspended"]
VEHICLE_TYPES      = ["Private Car", "Motorcycle", "Public Utility Vehicle",
                      "Truck", "Bus"]

# ── Palette ───────────────────────────────────────────────────
C = {
    # Sidebar
    "sidebar_bg":        "#0A1A3E",
    "sidebar_btn":       "#122350",
    "sidebar_btn_hov":   "#1B3370",
    "sidebar_sel":       "#1D4ED8",
    "sidebar_text":      "#FFFFFF",
    "sidebar_muted":     "#8BA3CC",
    "sidebar_accent":    "#F5C518",

    # Main area
    "bg":                "#F0F4FA",
    "card":              "#FFFFFF",
    "card_border":       "#D1DCF0",
    "header_text":       "#0A1A3E",
    "body_text":         "#1E293B",
    "muted_text":        "#64748B",

    # Status
    "success":           "#16A34A",
    "error":             "#DC2626",
    "warn":              "#D97706",

    # Accent buttons
    "btn_primary":       "#1D4ED8",
    "btn_primary_hov":   "#1E40AF",
    "btn_danger":        "#DC2626",
    "btn_danger_hov":    "#991B1B",
    "btn_secondary":     "#334155",
    "btn_secondary_hov": "#1E293B",

    # Tiles
    "tile_driver":       "#1D4ED8",
    "tile_vehicle":      "#059669",
    "tile_reg":          "#D97706",
    "tile_vio":          "#DC2626",

    # Table
    "tbl_header_bg":     "#0A1A3E",
    "tbl_header_fg":     "#FFFFFF",
    "tbl_row_even":      "#F8FAFF",
    "tbl_row_odd":       "#FFFFFF",
    "tbl_select":        "#DBEAFE",
    "tbl_border":        "#CBD5E1",
}

# ── Fonts (lazy-loaded after root window exists) ──────────────
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

def FONT_TITLE():   return _f("title")
def FONT_SECTION(): return _f("section")
def FONT_LABEL():   return _f("label")
def FONT_SMALL():   return _f("small")

FONT_MONO = ("Courier New", 11)
