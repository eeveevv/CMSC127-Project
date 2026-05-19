"""
db/helpers.py
Shared internal utilities used by all db sub-modules.
"""

import datetime


def _calc_age(dob_date: datetime.date) -> int:
    today = datetime.date.today()
    age = today.year - dob_date.year
    if (today.month, today.day) < (dob_date.month, dob_date.day):
        age -= 1
    return age


def _parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s.strip(), "%Y-%m-%d").date()
