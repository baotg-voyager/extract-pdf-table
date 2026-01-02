#!/usr/bin/env python3
"""
PDF Test Data Generator
Generates test PDFs by duplicating template pages and editing employee names/IDs
directly in the content stream using pikepdf for pixel-perfect accuracy.

This tool handles:
- Decompressing PDF content streams
- CID to Unicode font mapping
- Finding and replacing CID-encoded text
- Maintaining PDF structure and table layouts
- Preserving Camelot table extraction compatibility
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pikepdf


class PDFTestDataGenerator:
    """Generates test PDFs from a template by duplicating and editing pages."""
    
    def __init__(self, template_path: str):
        """
        Initialize the generator with a template PDF.
        
        Args:
            template_path: Path to the template PDF file
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template PDF not found: {template_path}")
        
        self.pdf = pikepdf.open(template_path)
        self.total_pages = len(self.pdf.pages)
        
        # Extract font mappings for text replacement
        self.font_mappings = self._extract_font_mappings()
        
    def _extract_font_mappings(self) -> Dict[str, Dict[int, str]]:
        """
        Extract ToUnicode mappings for all fonts in the document.
        
        Returns:
            Dictionary {font_name: {cid: unicode_char}}
        """
        mappings = {}
        
        # Check fonts in first page with content
        for page in self.pdf.pages:
            if '/Resources' not in page:
                continue
            
            resources = page.Resources
            if '/Font' not in resources:
                continue
            
            fonts_dict = dict(resources.Font)
            
            for font_name, font_obj in fonts_dict.items():
                if font_name in mappings:
                    continue  # Already extracted
                
                font_mappings = {}
                
                # Check for ToUnicode CMap
                if '/ToUnicode' in font_obj:
                    try:
                        to_unicode_stream = font_obj['/ToUnicode']
                        to_unicode_data = to_unicode_stream.read_bytes()
                        to_unicode_text = to_unicode_data.decode('latin-1', errors='ignore')
                        
                        # Parse CID to Unicode mappings
                        # Pattern: <XXXX> <YYYY>
                        pattern = r'<([0-9a-fA-F]+)>\s+<([0-9a-fA-F]+)>'
                        for match in re.finditer(pattern, to_unicode_text):
                            cid_hex, unicode_hex = match.groups()
                            try:
                                cid = int(cid_hex, 16)
                                unicode_val = int(unicode_hex, 16)
                                unicode_char = chr(unicode_val)
                                font_mappings[cid] = unicode_char
                            except:
                                pass
                    except Exception as e:
                        print(f"Warning: Could not extract ToUnicode for {font_name}: {e}")
                
                if font_mappings:
                    mappings[font_name] = font_mappings
        
        return mappings
        
    def get_content_stream(self, page_index: int) -> str:
        """
        Extract and decompress the content stream from a page.
        
        Args:
            page_index: Index of the page (0-based)
            
        Returns:
            The decompressed content stream as a string
        """
        page = self.pdf.pages[page_index]
        content = page.Contents
        
        if isinstance(content, pikepdf.Array):
            # Multiple content streams - get the first one
            stream = content[0]
            data = stream.read_bytes()
        else:
            # Single content stream
            data = content.read_bytes()
        
        # Decompress and decode
        return data.decode('latin-1', errors='ignore')
    
    def text_to_cid_sequence(self, text: str, font_mappings: Dict[int, str]) -> Optional[str]:
        """
        Convert text to CID sequence using font mappings.
        Reverses the ToUnicode mapping to find CID values.
        
        Args:
            text: The text to convert
            font_mappings: The CID to Unicode mapping from a font
            
        Returns:
            Hex-encoded CID sequence like <0001><0002> or None if cannot convert
        """
        if not font_mappings:
            return None
        
        # Reverse the mapping: Unicode char -> CID
        reverse_mapping = {v: k for k, v in font_mappings.items()}
        
        cid_sequence = ""
        for char in text:
            if char in reverse_mapping:
                cid = reverse_mapping[char]
                cid_sequence += f"<{cid:04X}>"
            else:
                # Character not in font, cannot convert
                return None
        
        return cid_sequence
    
    def find_text_in_content(self, content: str, text: str) -> List[str]:
        """
        Find all hex-encoded representations of text in PDF content.
        
        Args:
            content: The PDF content stream
            text: The text to find
            
        Returns:
            List of found CID hex patterns
        """
        patterns = []
        
        # Try to find text encoded in different fonts
        for font_name, font_map in self.font_mappings.items():
            cid_hex = self.text_to_cid_sequence(text, font_map)
            if cid_hex and cid_hex in content:
                patterns.append(cid_hex)
        
        return patterns
    
    def replace_text_in_content(
        self, 
        content: str, 
        replacements: Dict[str, str]
    ) -> str:
        """
        Replace text in PDF content stream using CID mappings.
        
        Args:
            content: The PDF content stream
            replacements: Dictionary of {old_text: new_text}
            
        Returns:
            Modified content stream
        """
        result = content
        
        for old_text, new_text in replacements.items():
            if not old_text or not new_text:
                continue
            
            # Find CID patterns for old text in any font
            for font_name, font_map in self.font_mappings.items():
                old_cid_hex = self.text_to_cid_sequence(old_text, font_map)
                new_cid_hex = self.text_to_cid_sequence(new_text, font_map)
                
                if old_cid_hex and new_cid_hex and old_cid_hex in result:
                    # Replace all occurrences
                    count = result.count(old_cid_hex)
                    result = result.replace(old_cid_hex, new_cid_hex)
                    if count > 0:
                        print(f"  Replaced ({font_name}): {old_text} → {new_text} ({count} occurrences)")
        
        return result
    
    def create_page_with_replacements(
        self,
        source_pdf: pikepdf.Pdf,
        source_page_index: int,
        replacements: Dict[str, str]
    ) -> None:
        """
        Duplicate a source page with replacements and append to PDF.
        
        Args:
            source_pdf: The source PDF object
            source_page_index: Index of page to duplicate
            replacements: Dictionary of {old_text: new_text}
        """
        source_page = source_pdf.pages[source_page_index]
        
        # Get the content and create a modified version
        content = self.get_content_stream(source_page_index)
        modified_content = self.replace_text_in_content(content, replacements)
        
        # Create a new content stream
        new_content_stream = pikepdf.Stream(source_pdf, modified_content.encode('latin-1'))
        
        # Use pikepdf's built-in method to duplicate the page
        # This ensures proper Page object creation
        new_page = source_pdf.pages[source_page_index]
        
        # Manually update the content of the duplicated page
        # We need to insert a new page and then update its content
        source_pdf.pages.append(source_pdf.pages[source_page_index])
        
        # Get the newly appended page and modify its content
        appended_page = source_pdf.pages[-1]
        appended_page.Contents = new_content_stream
    
    def generate_test_pdf(
        self,
        output_path: str,
        test_data: List[Dict[str, str]],
        template_page_index: int = -1,
        keep_original_first_page: bool = True
    ) -> None:
        """
        Generate a test PDF with duplicated pages and modified employee data.
        
        Args:
            output_path: Path for output PDF
            test_data: List of dicts with employee replacements
                      e.g., [{'240631': '250632'}, ...]
            template_page_index: Which page to use as template (-1 = last page)
            keep_original_first_page: If True, keep original pages before adding duplicates
        """
        if not test_data:
            raise ValueError("test_data cannot be empty")
        
        # Create output PDF starting from template
        output_pdf = pikepdf.open(str(self.template_path))
        
        # Normalize template page index
        if template_page_index < 0:
            template_page_index = len(self.pdf.pages) + template_page_index
        
        if template_page_index >= len(self.pdf.pages):
            raise ValueError(f"Template page {template_page_index} out of range")
        
        # Add duplicated pages with modifications
        for i, employee_data in enumerate(test_data):
            if i == 0 and keep_original_first_page:
                # Keep the first set of original pages
                continue
            
            print(f"Creating page {i + 1}...")
            self.create_page_with_replacements(
                output_pdf,
                template_page_index,
                employee_data
            )
        
        # Save output
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_pdf.save(output_path)
        
        print(f"✓ Generated test PDF: {output_path}")
        print(f"  Total pages: {len(output_pdf.pages)}")
        print(f"  Template page used: {template_page_index}")
    
    def close(self) -> None:
        """Close the PDF."""
        self.pdf.close()


def main():
    """Example usage of the PDF generator with real employee data."""
    template_path = "materials/出勤簿 - shukkinbo - attendance book.pdf"
    
    print("=== PDF Test Data Generator ===\n")
    print(f"Template: {template_path}\n")
    
    # Real employee data
    employees = [
        {"employee_id": "240631", "name": "工藤 貴幸"},
        {"employee_id": "250632", "name": "渡辺 雄次"},
        {"employee_id": "250633", "name": "奥山 広志"},
        {"employee_id": "250634", "name": "安井 直樹"},
    ]
    
    try:
        generator = PDFTestDataGenerator(template_path)
        print(f"✓ Loaded template with {generator.total_pages} pages")
        print(f"✓ Extracted font mappings for {len(generator.font_mappings)} fonts\n")
        
        # Example 1: Generate PDF with all employees (duplicate pages with their names/IDs)
        print("Example 1: Generating PDF with all employees...\n")
        
        test_data_all_employees = [
            {},  # Keep original template as page 0-7
        ]
        
        # For each employee after the first, create a replacemententry
        # Replace the first employee's ID with each employee's ID
        first_employee_id = employees[0]["employee_id"]
        
        for emp in employees[1:]:
            test_data_all_employees.append({
                first_employee_id: emp["employee_id"],
            })
        
        generator.generate_test_pdf(
            output_path="output/test_generated_all_employees.pdf",
            test_data=test_data_all_employees,
            template_page_index=-1  # Use last page as template
        )
        
        # Example 2: Generate individual test PDFs for each employee
        print("\n\nExample 2: Generating individual PDFs for each employee...\n")
        
        for emp in employees:
            test_data = [
                {
                    first_employee_id: emp["employee_id"],
                }
            ]
            
            output_filename = f"output/test_employee_{emp['employee_id']}.pdf"
            print(f"Generating {output_filename}...")
            
            generator.generate_test_pdf(
                output_path=output_filename,
                test_data=test_data,
                template_page_index=-1,
                keep_original_first_page=False  # Don't keep original
            )
        
        generator.close()
        
        print("\n✓ Test PDF generation complete!")
        print("\nGenerated files:")
        print("  - output/test_generated_all_employees.pdf (all employees in one PDF)")
        for emp in employees:
            print(f"  - output/test_employee_{emp['employee_id']}.pdf ({emp['name']})")
        
        print("\nYou can now use Camelot to extract table data and verify the PDFs are correct!")
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()