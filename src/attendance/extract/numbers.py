"""
Number extraction utilities for attendance parser
"""

import re
import pandas as pd


def extract_all_numbers(text):
    """Extract all integers from text, removing commas and spaces"""
    if not text or pd.isna(text):
        return []
    text_str = str(text).replace(',', '').replace(' ', '')
    numbers = re.findall(r'\d+', text_str)
    return [int(n) for n in numbers]


def is_spaced_digit_garbage(text):
    """Check if text is a spaced-digit garbage pattern like '1 0 0', '1 8 0', '0 0 0'"""
    text = text.strip()
    if not text:
        return False
    parts = text.split()
    if len(parts) >= 2:
        return all(len(p) <= 2 and p.isdigit() for p in parts)
    return False


def extract_count_from_spaced_garbage(text):
    """
    Extract potential count from spaced-digit pattern.
    Pattern like '1 8 0' may have count=8 (middle digit).
    """
    text = text.strip()
    parts = text.split()
    if len(parts) >= 2:
        digits = [int(p) for p in parts if p.isdigit()]
        if len(digits) >= 3 and digits[-1] == 0:
            if digits[0] in [0, 1] and digits[1] > 0:
                return digits[1]
    return None
