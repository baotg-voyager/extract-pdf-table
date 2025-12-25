"""
Employee extraction for attendance parser
"""

import re


# Keywords to exclude when extracting employee names
# These are attendance status markers, not name components
ATTENDANCE_KEYWORDS_TO_SKIP = [
    '出勤',   # Work day
    '公休',   # Public holiday
    '有給',   # Paid leave
    '欠勤',   # Absence
    '遅刻',   # Late arrival
    '早退',   # Early departure
    '運転手', # Driver
    '無欠'    # No absence
]


def _cell_contains_employee_id(cell_content):
    """
    Check if a cell contains a 6-digit employee ID.
    
    Args:
        cell_content: String content of the cell
    
    Returns:
        True if cell contains employee ID pattern, False otherwise
    """
    return re.search(r'\b(\d{6})\b', str(cell_content)) is not None


def _scan_row_for_employee_id(table_dataframe, row_index):
    """
    Scan first 3 columns of a row to find employee ID.
    
    Args:
        table_dataframe: DataFrame from the table
        row_index: Index of the row to scan
    
    Returns:
        Column index where employee ID was found, or None
    """
    for column_index in range(min(3, len(table_dataframe.columns))):
        current_cell_content = str(table_dataframe.iloc[row_index, column_index])
        if _cell_contains_employee_id(current_cell_content):
            return column_index
    return None


def find_employee_rows_in_table(table_dataframe):
    """
    Locate all employee records in a table by searching for 6-digit employee IDs.
    
    Employee IDs are always present in the first 3 columns of each employee's row.
    Returns a list of row indices where employees are found.
    
    Args:
        table_dataframe: DataFrame from a single table in the PDF
    
    Returns:
        List of row indices containing employee records
    """
    employee_row_indices = []
    
    # Scan each row for employee ID
    for row_index in range(len(table_dataframe)):
        if _scan_row_for_employee_id(table_dataframe, row_index) is not None:
            employee_row_indices.append(row_index)
    
    return employee_row_indices


def _extract_employee_id_from_cell(cell_content):
    """
    Extract 6-digit employee ID from cell content.
    
    Args:
        cell_content: String content of the cell
    
    Returns:
        Employee ID string or None if not found
    """
    employee_id_match = re.search(r'\b(\d{6})\b', str(cell_content))
    return employee_id_match.group(1) if employee_id_match else None


def _is_valid_name_line(text_line):
    """
    Check if a text line is a valid name (not a keyword or marker).
    
    Args:
        text_line: Single line of text to check
    
    Returns:
        True if line could be a name, False if it's a keyword or marker
    """
    if text_line in ATTENDANCE_KEYWORDS_TO_SKIP:
        return False
    if re.match(r'^[A-Z0-9ｱ-ﾝァ-ヶー]+$', text_line):
        return False
    return True


def _extract_name_from_line(text_line):
    """
    Extract Japanese name from a text line.
    
    Args:
        text_line: Single line of text to parse
    
    Returns:
        Name string if found, None otherwise
    """
    name_match = re.search(r'([一-龯ぁ-んァ-ヶー]+\s+[一-龯ぁ-んァ-ヶー]+)', text_line)
    return name_match.group(1).strip() if name_match else None


def _extract_name_from_cell_content(cell_content):
    """
    Extract employee name from cell content by scanning lines.
    
    Cell may contain multiple lines (ID, name, attendance markers).
    This function filters out keywords and extracts the actual name.
    
    Args:
        cell_content: String content of the cell (may contain newlines)
    
    Returns:
        Name string or None if not found
    """
    cell_text_lines = str(cell_content).split('\n')
    
    for text_line in cell_text_lines:
        text_line = text_line.strip()
        
        # Skip attendance keywords and non-Japanese markers
        if not _is_valid_name_line(text_line):
            continue
        
        # Try to extract name from this line
        extracted_name = _extract_name_from_line(text_line)
        if extracted_name:
            return extracted_name
    
    return None


def _find_cell_with_employee_id(table_dataframe, employee_row_index):
    """
    Find which cell in first 3 columns contains the employee ID.
    
    Args:
        table_dataframe: DataFrame containing the row
        employee_row_index: Index of the employee row
    
    Returns:
        Tuple of (column_index, cell_content) or (None, None) if not found
    """
    for column_index in range(min(3, len(table_dataframe.columns))):
        current_cell_content = str(table_dataframe.iloc[employee_row_index, column_index])
        if _cell_contains_employee_id(current_cell_content):
            return column_index, current_cell_content
    return None, None


def extract_employee_id_and_name(table_dataframe, employee_row_index):
    """
    Extract employee ID and name from a row.
    
    The row contains an employee ID (6 digits) and a full name (usually two kanji).
    We filter out attendance keywords and non-Japanese text to find the actual name.
    
    Args:
        table_dataframe: DataFrame containing the row
        employee_row_index: Row index of the employee record
    
    Returns:
        Tuple of (employee_id, name) or (None, None) if extraction fails
    """
    # Find the cell containing employee ID
    cell_column_index, cell_content = _find_cell_with_employee_id(table_dataframe, employee_row_index)
    
    if cell_column_index is None:
        return None, None
    
    # Extract employee ID from the cell
    extracted_employee_id = _extract_employee_id_from_cell(cell_content)
    
    # Extract name from the same cell
    extracted_employee_name = _extract_name_from_cell_content(cell_content)
    
    return extracted_employee_id, extracted_employee_name


def _is_numeric_line(text_line):
    """
    Check if a text line contains only digits.
    
    Args:
        text_line: Text line to check
    
    Returns:
        True if line is numeric, False otherwise
    """
    return text_line and re.match(r'^\d+$', text_line) is not None


def _is_in_valid_shukkin_range(current_number):
    """
    Check if number is in valid working days range (20-31).
    
    Args:
        current_number: Integer to check
    
    Returns:
        True if in range 20-31, False otherwise
    """
    return 20 <= current_number <= 31


def _is_valid_kokyu_count(current_number):
    """
    Check if number is a valid kokyu (holiday) count (≤10).
    
    Args:
        current_number: Integer to check
    
    Returns:
        True if in range 0-10, False otherwise
    """
    return current_number <= 10


def _parse_shukkin_count(current_number, found_shukkin_value):
    """
    Try to extract shukkin count from a number.
    
    Args:
        current_number: Candidate number
        found_shukkin_value: Whether shukkin has already been found
    
    Returns:
        Tuple of (shukkin_count, was_found) or (0, False) if not found
    """
    if not found_shukkin_value and _is_in_valid_shukkin_range(current_number):
        return current_number, True
    return 0, False


def _parse_kokyu_count(current_number, found_kokyu_keyword):
    """
    Try to extract kokyu count from a number.
    
    Args:
        current_number: Candidate number
        found_kokyu_keyword: Whether 公休 keyword was found
    
    Returns:
        Tuple of (kokyu_count, should_stop_parsing)
    """
    if found_kokyu_keyword and _is_valid_kokyu_count(current_number):
        return current_number, True
    return 0, False


def parse_attendance_counts_from_salary_data(combined_column6_text):
    """
    Extract shukkin (working days) and kokyu (public holidays) counts from salary data.
    
    These appear in a specific pattern in column 6:
    - '出勤' marker followed by a count (20-31, typically 20-22 working days)
    - '公休' marker followed by a count (≤10 holidays)
    
    Why: We need to know how many days the employee actually worked vs. holidays.
    
    Args:
        combined_column6_text: All column 6 rows joined together
    
    Returns:
        Tuple of (shukkin_count, kokyu_count)
    """
    shukkin_days = 0
    kokyu_days = 0
    found_shukkin_value = False
    found_kokyu_keyword = False
    
    text_lines = combined_column6_text.split('\n')
    
    # Scan first 25 lines of salary data for attendance information
    for text_line in text_lines[:25]:
        text_line = text_line.strip()
        
        # Check for attendance markers
        if text_line == '出勤':
            continue
        elif text_line == '公休':
            found_kokyu_keyword = True
            continue
        
        # Process numeric values
        if _is_numeric_line(text_line):
            current_number = int(text_line)
            
            # Try to extract shukkin count
            extracted_shukkin, found_shukkin_value = _parse_shukkin_count(current_number, found_shukkin_value)
            if found_shukkin_value:
                shukkin_days = extracted_shukkin
            
            # Try to extract kokyu count
            extracted_kokyu, should_stop = _parse_kokyu_count(current_number, found_kokyu_keyword)
            if should_stop:
                kokyu_days = extracted_kokyu
                break  # Stop parsing once we have both values
    
    return shukkin_days, kokyu_days


def _extract_time_from_cell(cell_content):
    """
    Extract time in HH:MM format from cell content.
    
    Args:
        cell_content: String content to search
    
    Returns:
        Time string in HH:MM format or None if not found
    """
    if '稼働時間' not in cell_content:
        return None
    
    working_hours_match = re.search(r'(\d+:\d+)', cell_content)
    return working_hours_match.group(1) if working_hours_match else None


def extract_working_hours_from_salary_rows(salary_column_rows):
    """
    Extract working hours (稼働時間) from column 6 rows.
    
    Args:
        salary_column_rows: List of column 6 cell contents
    
    Returns:
        String in HH:MM format or empty string if not found
    """
    for column6_cell_content in salary_column_rows:
        extracted_time = _extract_time_from_cell(column6_cell_content)
        if extracted_time:
            return extracted_time
    
    return ""
