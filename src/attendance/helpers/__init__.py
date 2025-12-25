"""Helper functions for attendance PDF parsing"""

from .validation import validate_pdf_tables
from .table import process_table
from .employee import (
    process_employee_in_table,
    build_employee_record,
)
from .extraction import extract_attendance_and_salary_data
from .utils import (
    table_has_salary_column,
    determine_employee_data_range,
)

__all__ = [
    'validate_pdf_tables',
    'table_has_salary_column',
    'determine_employee_data_range',
    'process_table',
    'process_employee_in_table',
    'build_employee_record',
    'extract_attendance_and_salary_data',
]
