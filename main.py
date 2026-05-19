"""
main.py
LTO Information Management System — Entry Point
CMSC 127 | 2nd Semester AY 2025-2026

Run:  python main.py
"""

import customtkinter as ctk
from ui.app import LTOApp

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = LTOApp()
    app.mainloop()
