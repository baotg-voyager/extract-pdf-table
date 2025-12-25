"""Employee record helpers for PDF parsing"""

from ..extract import (
    extract_employee_id_and_name,
    extract_column6_salary_data,
)
from .utils import table_has_salary_column, determine_employee_data_range
from .extraction import extract_attendance_and_salary_data


def process_employee_in_table(table_dataframe, employee_sequence_index, employee_row_index, employee_row_indices):
    """
    Process a single employee record from a table.
    
    Args:
        table_dataframe: DataFrame from the table
        employee_sequence_index: Position in employee list
        employee_row_index: Row index of this employee
        employee_row_indices: All employee row indices
    
    Returns:
        Employee record dictionary or None if employee should be skipped
    """
    # Extract basic employee info
    employee_id, employee_name = extract_employee_id_and_name(table_dataframe, employee_row_index)
    
    if not employee_id:
        return None
    
    print(f"    Employee: {employee_id} - {employee_name}")
    
    # Ensure table has salary data column
    if not table_has_salary_column(table_dataframe):
        return None
    
    # Determine data range for this employee
    employee_data_start_row_index, employee_data_end_row_index = determine_employee_data_range(
        employee_sequence_index, employee_row_index, employee_row_indices, table_dataframe
    )
    
    # Extract column 6 salary data for this employee
    extracted_salary_rows, extracted_working_hours = extract_column6_salary_data(
        table_dataframe, employee_data_start_row_index, employee_data_end_row_index
    )
    
    # Extract attendance and salary data
    parsed_shukkin_count, parsed_kokyu_count, extracted_salary_fields = extract_attendance_and_salary_data(
        extracted_salary_rows
    )
    
    # Assemble and return complete employee record
    return build_employee_record(
        employee_id, employee_name, extracted_working_hours, 
        parsed_shukkin_count, parsed_kokyu_count, extracted_salary_fields
    )


def build_employee_record(employee_id, employee_name, extracted_working_hours, parsed_shukkin_count, 
                          parsed_kokyu_count, extracted_salary_fields):
    """
    Assemble complete employee record from extracted data.
    
    Args:
        employee_id: Employee ID string
        employee_name: Employee name string
        extracted_working_hours: Working hours in HH:MM format
        parsed_shukkin_count: Number of working days
        parsed_kokyu_count: Number of holidays
        extracted_salary_fields: Dictionary of salary field data
    
    Returns:
        Dictionary containing complete employee record
    """
    total_salary_amount = extracted_salary_fields['total_amount']['amount']
    
    return {
        'employee_id': employee_id,
        'name': employee_name if employee_name else "",
        'shukkin': {'count': max(parsed_shukkin_count, 0), 'amount': 0},
        'kokyu': {'count': max(parsed_kokyu_count, 0), 'amount': 0},
        'kado_jikan': extracted_working_hours,
        'kihon_kyu': extracted_salary_fields['base_salary'],
        'hosho_zangyo': extracted_salary_fields['guaranteed_overtime'],
        'josha_teate': extracted_salary_fields['commute_allowance'],
        'sagawa_warimashi_teate': extracted_salary_fields['sagawa_markup_allowance'],
        'double_teate': extracted_salary_fields['double_allowance'],
        'rinji_teate': extracted_salary_fields['temp_allowance'],
        'yakin_teate': extracted_salary_fields['night_shift_allowance'],
        'kyujitsu_teate': extracted_salary_fields['holiday_allowance'],
        'chokyori_teate': extracted_salary_fields['longdist_allowance'],
        'sonota': extracted_salary_fields['other_allowance'],
        'kei': total_salary_amount
    }
