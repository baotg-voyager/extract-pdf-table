"""Validation helpers for PDF parsing"""


def validate_pdf_tables(extracted_pdf_tables):
    """
    Validate that PDF tables were extracted successfully.
    
    Args:
        extracted_pdf_tables: List of table objects from Camelot
    
    Raises:
        ValueError: If no tables found in PDF
    """
    if not extracted_pdf_tables or len(extracted_pdf_tables) == 0:
        raise ValueError("No tables found in PDF")
