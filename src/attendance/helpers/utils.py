"""Utility helpers for table and employee processing"""


def table_has_salary_column(table_dataframe):
    """
    Check if table has salary data column (column 6).
    
    Args:
        table_dataframe: DataFrame from the table
    
    Returns:
        True if column 6 exists, False otherwise
    """
    return len(table_dataframe.columns) > 6


def determine_employee_data_range(employee_sequence_index, employee_row_index, employee_row_indices, table_dataframe):
    """
    Calculate data range for this employee.
    
    Each employee's data spans ~14 rows until the next employee.
    
    Args:
        employee_sequence_index: Position in employee list
        employee_row_index: Row index of this employee
        employee_row_indices: All employee row indices
        table_dataframe: DataFrame to get row count
    
    Returns:
        Tuple of (start_row_index, end_row_index)
    """
    employee_data_start_row_index = employee_row_index
    
    if employee_sequence_index + 1 < len(employee_row_indices):
        # Next employee exists, use its row as boundary
        employee_data_end_row_index = employee_row_indices[employee_sequence_index + 1]
    else:
        # Last employee, assume 14 rows of data
        employee_data_end_row_index = min(employee_row_index + 14, len(table_dataframe))
    
    return employee_data_start_row_index, employee_data_end_row_index
