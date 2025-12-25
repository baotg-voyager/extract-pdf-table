"""Data extraction helpers for PDF parsing"""

from ..extract import (
    parse_attendance_counts_from_salary_data,
    extract_all_salary_field_components,
)


def extract_attendance_and_salary_data(extracted_salary_rows):
    """
    Extract attendance counts and salary field components.
    
    Args:
        extracted_salary_rows: List of column 6 cell contents
    
    Returns:
        Tuple of (parsed_shukkin_count, parsed_kokyu_count, extracted_salary_fields)
    """
    # Parse attendance counts from salary data
    combined_salary_column_text = '\n'.join(extracted_salary_rows)
    parsed_shukkin_count, parsed_kokyu_count = parse_attendance_counts_from_salary_data(
        combined_salary_column_text
    )
    
    # Extract all salary field components
    extracted_salary_fields = extract_all_salary_field_components(extracted_salary_rows)
    
    return parsed_shukkin_count, parsed_kokyu_count, extracted_salary_fields
