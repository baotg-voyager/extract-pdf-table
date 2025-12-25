"""Table-level helpers for PDF parsing"""

from ..extract import find_employee_rows_in_table
from .employee import process_employee_in_table


def process_table(table_object, table_sequence_index, total_tables):
    """
    Process all employees in a single table.
    
    Args:
        table_object: Camelot table object
        table_sequence_index: Position in table list
        total_tables: Total number of tables
    
    Returns:
        List of employee records from this table
    """
    table_dataframe = table_object.df
    print(f"Processing table {table_sequence_index + 1}/{total_tables}, shape: {table_dataframe.shape}")
    
    # Find all employee records in this table
    employee_row_indices = find_employee_rows_in_table(table_dataframe)
    print(f"  Found {len(employee_row_indices)} employees at rows: {employee_row_indices}")
    
    table_employee_records = []
    
    # Process each employee in the table
    for employee_sequence_index, employee_row_index in enumerate(employee_row_indices):
        employee_record = process_employee_in_table(
            table_dataframe, employee_sequence_index, employee_row_index, employee_row_indices
        )
        
        if employee_record is not None:
            table_employee_records.append(employee_record)
    
    return table_employee_records
