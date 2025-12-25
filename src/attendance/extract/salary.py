"""
Salary field extraction for attendance parser
"""

import re
from .numbers import extract_all_numbers, is_spaced_digit_garbage, extract_count_from_spaced_garbage


FIELD_LABELS = [
    "基 本 給", "基本給", "保障残業", "乗車手当", "佐川割増手当",
    "ダブル手当", "臨時手当", "夜勤手当", "休日手当", "長距離手当",
    "その他", "計", "稼働時間"
]

# Fields that require special garbage pattern handling
FIELDS_WITH_GARBAGE_PATTERNS = ['長距離手当', 'その他', '休日手当']


def _is_field_with_special_handling(field_label):
    """Check if field requires special garbage pattern handling."""
    return field_label in FIELDS_WITH_GARBAGE_PATTERNS


def _extract_garbage_count_from_parts(parts_list):
    """
    Extract count from spaced-digit garbage patterns in parts list.
    
    Args:
        parts_list: List of text parts from row data
    
    Returns:
        Tuple of (garbage_count, clean_parts_list)
    """
    garbage_count = None
    clean_parts = []
    
    for part in parts_list:
        if is_spaced_digit_garbage(part):
            extracted = extract_count_from_spaced_garbage(part)
            if extracted is not None:
                garbage_count = extracted
        else:
            clean_parts.append(part)
    
    return garbage_count, clean_parts


def _extract_longdist_allowance_result(all_nums, garbage_count):
    """
    Extract count and amount for 長距離手当 field.
    
    Args:
        all_nums: List of extracted numbers
        garbage_count: Count from garbage pattern or None
    
    Returns:
        Dictionary with count and amount
    """
    # Empty or all zeros
    if len(all_nums) == 0 or (len(all_nums) <= 2 and all(n == 0 for n in all_nums)):
        return {'count': 0, 'amount': 0}
    
    # Two or more numbers: last two are count and amount
    if len(all_nums) >= 2:
        return {'count': all_nums[-2], 'amount': all_nums[-1]}
    
    # Single number: use garbage count if available
    if len(all_nums) == 1:
        if garbage_count is not None:
            return {'count': garbage_count, 'amount': all_nums[0]}
        return {'count': 0, 'amount': all_nums[0]}
    
    return {'count': 0, 'amount': 0}


def _extract_other_allowance_result(all_nums):
    """
    Extract count and amount for その他 field.
    
    Args:
        all_nums: List of extracted numbers
    
    Returns:
        Dictionary with count and amount
    """
    # Empty or all zeros
    if len(all_nums) == 0 or (len(all_nums) <= 2 and all(n == 0 for n in all_nums)):
        return {'count': 0, 'amount': 0}
    
    # Two or more numbers: last two are count and amount
    if len(all_nums) >= 2:
        return {'count': all_nums[-2], 'amount': all_nums[-1]}
    
    # Single number: no count
    if len(all_nums) == 1:
        return {'count': 0, 'amount': all_nums[0]}
    
    return {'count': 0, 'amount': 0}


def _extract_holiday_allowance_result(all_nums):
    """
    Extract count and amount for 休日手当 field.
    
    Special rule: count = amount / 2600
    
    Args:
        all_nums: List of extracted numbers
    
    Returns:
        Dictionary with count and amount
    """
    if len(all_nums) >= 1:
        amount = all_nums[-1]
        count = amount // 2600 if amount > 0 else 0
        return {'count': count, 'amount': amount}
    
    return {'count': 0, 'amount': 0}


def _extract_special_field_result(field_label, all_nums, garbage_count):
    """
    Extract result for fields with special handling.
    
    Args:
        field_label: Name of the salary field
        all_nums: List of extracted numbers
        garbage_count: Count from garbage pattern
    
    Returns:
        Dictionary with count and amount, or None if field not handled
    """
    if field_label == '長距離手当':
        return _extract_longdist_allowance_result(all_nums, garbage_count)
    elif field_label == 'その他':
        return _extract_other_allowance_result(all_nums)
    elif field_label == '休日手当':
        return _extract_holiday_allowance_result(all_nums)
    
    return None


def _extract_standard_field_result(all_nums):
    """
    Extract count and amount using standard extraction rules.
    
    Args:
        all_nums: List of extracted numbers
    
    Returns:
        Dictionary with count and amount
    """
    if len(all_nums) >= 2:
        return {'count': all_nums[-2], 'amount': all_nums[-1]}
    elif len(all_nums) == 1:
        return {'count': 0, 'amount': all_nums[0]}
    else:
        return {'count': 0, 'amount': 0}


def _find_field_in_rows(rows_data, field_label):
    """
    Find which row contains the field label.
    
    Args:
        rows_data: List of row data strings
        field_label: Label to search for
    
    Returns:
        Row data containing the label, or None if not found
    """
    for row_data in rows_data:
        if field_label in row_data:
            return row_data
    return None


def extract_salary_field_from_rows(rows_data, field_label):
    """
    Extract count and amount for a salary field from a list of row data.
    
    Handles both formats:
    - Standard: 'label\\n...\\ncount\\namount' (label at start)
    - Reversed: '...\\ncount\\namount\\nlabel' (label at end)
    
    Args:
        rows_data: List of row data strings
        field_label: Label of the salary field to extract
    
    Returns:
        Dictionary with 'count' and 'amount' keys
    """
    # Find the row containing this field
    row_with_field = _find_field_in_rows(rows_data, field_label)
    if row_with_field is None:
        return {'count': 0, 'amount': 0}
    
    # Handle fields with special garbage patterns
    if _is_field_with_special_handling(field_label):
        parts = row_with_field.split('\n')
        garbage_count, clean_parts = _extract_garbage_count_from_parts(parts)
        clean_text = '\n'.join(clean_parts)
        all_nums = extract_all_numbers(clean_text)
        
        result = _extract_special_field_result(field_label, all_nums, garbage_count)
        if result is not None:
            return result
    
    # Standard extraction for other fields
    all_nums = extract_all_numbers(row_with_field)
    return _extract_standard_field_result(all_nums)


def _find_label_index_in_lines(lines, field_label):
    """
    Find the line index containing the field label.
    
    Args:
        lines: List of text lines
        field_label: Label to search for
    
    Returns:
        Index of line containing label, or None if not found
    """
    for idx, line in enumerate(lines):
        if field_label in line:
            return idx
    return None


def _is_another_field_label(line_text, current_field_label):
    """
    Check if a line contains a different field label.
    
    Args:
        line_text: Text to check
        current_field_label: Current field we're processing
    
    Returns:
        True if line is a different field label, False otherwise
    """
    for label in FIELD_LABELS:
        if label in line_text and label != current_field_label:
            return True
    return False


def _extract_numbers_after_label(lines, label_index, field_label):
    """
    Extract numbers from lines after the label line.
    
    Continues until hitting another field label.
    
    Args:
        lines: List of text lines
        label_index: Index where label was found
        field_label: Current field label
    
    Returns:
        List of extracted numbers
    """
    numbers = []
    
    for idx in range(label_index + 1, len(lines)):
        line = lines[idx].strip()
        
        # Stop if we hit another field label
        if _is_another_field_label(line, field_label):
            break
        
        line_numbers = extract_all_numbers(line)
        numbers.extend(line_numbers)
    
    return numbers


def extract_salary_field(col6_text, field_label):
    """
    Legacy function for combined text extraction.
    
    Args:
        col6_text: Combined text from column 6
        field_label: Label of the salary field to extract
    
    Returns:
        Dictionary with 'count' and 'amount' keys
    """
    lines = col6_text.split('\n')
    
    try:
        # Find label line
        label_index = _find_label_index_in_lines(lines, field_label)
        if label_index is None:
            return {'count': 0, 'amount': 0}
        
        # Try to extract numbers from label line
        label_line = lines[label_index]
        all_nums = extract_all_numbers(label_line)
        
        if len(all_nums) >= 2:
            return {'count': all_nums[-2], 'amount': all_nums[-1]}
        elif len(all_nums) == 1:
            return {'count': 0, 'amount': all_nums[0]}
        
        # Extract numbers from lines after label
        numbers = _extract_numbers_after_label(lines, label_index, field_label)
        return _extract_standard_field_result(numbers)
        
    except Exception as exception:
        print(f"  Error extracting {field_label}: {exception}")
        return {'count': 0, 'amount': 0}


def extract_column6_salary_data(table_dataframe, employee_start_row_index, employee_end_row_index):
    """
    Extract all salary data from column 6 for an employee.
    
    Column 6 contains structured salary information across multiple rows.
    We preserve the row-by-row structure to properly parse different field formats.
    Also extracts working hours (稼働時間) which appears in this column.
    
    Args:
        table_dataframe: DataFrame from the table
        employee_start_row_index: Starting row index for this employee
        employee_end_row_index: Ending row index for this employee
    
    Returns:
        Tuple of (salary_rows_list, working_hours_string)
    """
    extracted_working_hours = ""
    extracted_salary_rows = []
    
    # Scan column 6 from employee start to end row
    for row_index in range(employee_start_row_index, min(employee_end_row_index, len(table_dataframe))):
        column6_cell_content = str(table_dataframe.iloc[row_index, 6])
        extracted_salary_rows.append(column6_cell_content)
        
        # Look for working hours (時:分 format)
        if '稼働時間' in column6_cell_content:
            working_hours_match = re.search(r'(\d+:\d+)', column6_cell_content)
            if working_hours_match:
                extracted_working_hours = working_hours_match.group(1)
    
    return extracted_salary_rows, extracted_working_hours


def extract_all_salary_field_components(salary_column_rows):
    """
    Extract all salary components from column 6 rows.
    
    Why separate function: Salary fields need row-based extraction to handle
    different data formats (standard vs. reversed label placement).
    
    Args:
        salary_column_rows: List of column 6 cell contents
    
    Returns:
        Dictionary with counts and amounts for each salary component
    """
    return {
        'base_salary': extract_salary_field_from_rows(salary_column_rows, '基 本 給') or 
                      extract_salary_field_from_rows(salary_column_rows, '基本給'),
        'guaranteed_overtime': extract_salary_field_from_rows(salary_column_rows, '保障残業'),
        'commute_allowance': extract_salary_field_from_rows(salary_column_rows, '乗車手当'),
        'sagawa_markup_allowance': extract_salary_field_from_rows(salary_column_rows, '佐川割増手当'),
        'double_allowance': extract_salary_field_from_rows(salary_column_rows, 'ダブル手当'),
        'temp_allowance': extract_salary_field_from_rows(salary_column_rows, '臨時手当'),
        'night_shift_allowance': extract_salary_field_from_rows(salary_column_rows, '夜勤手当'),
        'holiday_allowance': extract_salary_field_from_rows(salary_column_rows, '休日手当'),
        'longdist_allowance': extract_salary_field_from_rows(salary_column_rows, '長距離手当'),
        'other_allowance': extract_salary_field_from_rows(salary_column_rows, 'その他'),
        'total_amount': extract_salary_field_from_rows(salary_column_rows, '計'),
    }


def extract_column6_salary_data(table_dataframe, employee_start_row_index, employee_end_row_index):
    """
    Extract all salary data from column 6 for an employee.
    
    Column 6 contains structured salary information across multiple rows.
    We preserve the row-by-row structure to properly parse different field formats.
    Also extracts working hours (稼働時間) which appears in this column.
    
    Args:
        table_dataframe: DataFrame from the table
        employee_start_row_index: Starting row index for this employee
        employee_end_row_index: Ending row index for this employee
    
    Returns:
        Tuple of (salary_rows_list, working_hours_string)
    """
    extracted_working_hours = ""
    extracted_salary_rows = []
    
    # Scan column 6 from employee start to end row
    for row_index in range(employee_start_row_index, min(employee_end_row_index, len(table_dataframe))):
        column6_cell_content = str(table_dataframe.iloc[row_index, 6])
        extracted_salary_rows.append(column6_cell_content)
        
        # Look for working hours (時:分 format)
        if '稼働時間' in column6_cell_content:
            working_hours_match = re.search(r'(\d+:\d+)', column6_cell_content)
            if working_hours_match:
                extracted_working_hours = working_hours_match.group(1)
    
    return extracted_salary_rows, extracted_working_hours


def extract_all_salary_field_components(salary_column_rows):
    """
    Extract all salary components from column 6 rows.
    
    Why separate function: Salary fields need row-based extraction to handle
    different data formats (standard vs. reversed label placement).
    
    Args:
        salary_column_rows: List of column 6 cell contents
    
    Returns:
        Dictionary with counts and amounts for each salary component
    """
    return {
        'base_salary': extract_salary_field_from_rows(salary_column_rows, '基 本 給') or 
                      extract_salary_field_from_rows(salary_column_rows, '基本給'),
        'guaranteed_overtime': extract_salary_field_from_rows(salary_column_rows, '保障残業'),
        'commute_allowance': extract_salary_field_from_rows(salary_column_rows, '乗車手当'),
        'sagawa_markup_allowance': extract_salary_field_from_rows(salary_column_rows, '佐川割増手当'),
        'double_allowance': extract_salary_field_from_rows(salary_column_rows, 'ダブル手当'),
        'temp_allowance': extract_salary_field_from_rows(salary_column_rows, '臨時手当'),
        'night_shift_allowance': extract_salary_field_from_rows(salary_column_rows, '夜勤手当'),
        'holiday_allowance': extract_salary_field_from_rows(salary_column_rows, '休日手当'),
        'longdist_allowance': extract_salary_field_from_rows(salary_column_rows, '長距離手当'),
        'other_allowance': extract_salary_field_from_rows(salary_column_rows, 'その他'),
        'total_amount': extract_salary_field_from_rows(salary_column_rows, '計'),
    }
