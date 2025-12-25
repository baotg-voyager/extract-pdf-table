"""
PDF Parser for attendance records using Camelot

This module orchestrates the extraction of employee attendance and salary data 
from PDF payroll tables. It uses helper functions from the extract submodule
to perform specific extraction tasks.

PDF structure:
- Multiple tables (one per day)
- Each table has 4 employees at fixed row positions
- Employee IDs in columns 0-2, salary data in column 6
"""

import camelot

from .helpers import (
    validate_pdf_tables,
    process_table,
)


def parse_pdf(pdf_path):
    """
    Parse PDF and extract all employee attendance and salary records.
    
    This is the main entry point for PDF parsing. It coordinates with helper
    functions in the helpers submodule to:
    1. Find employee records in each table
    2. Extract employee IDs and names
    3. Extract salary and attendance data from column 6
    4. Assemble complete employee records
    
    Args:
        pdf_path: Path to the attendance PDF file
    
    Returns:
        List of employee records, each containing ID, name, attendance counts,
        and salary components (count and amount for each field)
    """
    # Extract tables from PDF using lattice flavor for structured data
    extracted_pdf_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    
    # Validate extraction was successful
    validate_pdf_tables(extracted_pdf_tables)
    
    all_employee_records = []
    
    # Process each table in the PDF
    for table_sequence_index, table_object in enumerate(extracted_pdf_tables):
        table_employee_records = process_table(
            table_object, table_sequence_index, len(extracted_pdf_tables)
        )
        all_employee_records.extend(table_employee_records)
    
    return all_employee_records
