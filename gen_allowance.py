#!/usr/bin/env python3
"""
Driver Allowance PDF Test Data Generator
Generates test PDFs for driver allowance lists by duplicating the template page
and editing employee names/IDs directly in the content stream using pikepdf.

Features:
- Duplicates template pages with employee-specific data
- Edits content stream directly for pixel-perfect accuracy
- Maintains table layout and formatting
- Preserves Camelot table extraction compatibility
- Supports JSON input for employee data
- Default 40 employees or custom count
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pikepdf


class AllowancePDFGenerator:
    """Generates allowance test PDFs from a template by duplicating and editing pages."""
    
    # Default Japanese employee data
    DEFAULT_EMPLOYEES = [
        {"employee_id": "160013", "name": "江頭 孝之"},
        {"employee_id": "180201", "name": "中村 公一"},
        {"employee_id": "180209", "name": "中西 宏二"},
        {"employee_id": "180212", "name": "津端 晋治"},
        {"employee_id": "180602", "name": "大木 茂美"},
        {"employee_id": "180603", "name": "高藤 久也"},
        {"employee_id": "180605", "name": "松本 文人"},
        {"employee_id": "190213", "name": "楳澤 和行"},
        {"employee_id": "190607", "name": "関根 桐人"},
        {"employee_id": "200229", "name": "小林 智"},
        {"employee_id": "200233", "name": "石井 俊之"},
        {"employee_id": "210243", "name": "菅野 牧夫"},
        {"employee_id": "210609", "name": "山口 裕介"},
        {"employee_id": "220601", "name": "野原 大輔"},
        {"employee_id": "220603", "name": "坂本 裕一"},
        {"employee_id": "220608", "name": "牟田 豊"},
        {"employee_id": "220610", "name": "小鷲 恭平"},
        {"employee_id": "220612", "name": "神田 秀靖"},
        {"employee_id": "220614", "name": "天野 忠典"},
        {"employee_id": "220615", "name": "溝口 貴宏"},
        {"employee_id": "230616", "name": "増田 将昭"},
        {"employee_id": "230618", "name": "相馬 秀政"},
        {"employee_id": "230619", "name": "大久保 洋"},
        {"employee_id": "230620", "name": "岩切 慎吾"},
        {"employee_id": "230621", "name": "神戸 俊彦"},
        {"employee_id": "240623", "name": "関口 政章"},
        {"employee_id": "240625", "name": "佐藤 翼"},
        {"employee_id": "240629", "name": "安田 芳一"},
        {"employee_id": "240631", "name": "工藤 貴幸"},
        {"employee_id": "250632", "name": "渡辺 雄次"},
        {"employee_id": "250633", "name": "奥山 広志"},
        # Add 9 more variations for 40 total (cycling through names with ID variations)
        {"employee_id": "250634", "name": "安井 直樹"},
        {"employee_id": "250635", "name": "鈴木 太郎"},
        {"employee_id": "250636", "name": "田中 花子"},
        {"employee_id": "250637", "name": "佐藤 次郎"},
        {"employee_id": "250638", "name": "高橋 美咲"},
        {"employee_id": "250639", "name": "渡辺 健太"},
        {"employee_id": "250640", "name": "中田 由美"},
        {"employee_id": "250641", "name": "山田 拓也"},
        {"employee_id": "250642", "name": "伊藤 香里"},
        {"employee_id": "250643", "name": "佐々木 隆"},
    ]
    
    def __init__(self, template_path: str):
        """
        Initialize the generator with a template PDF.
        
        Args:
            template_path: Path to the template PDF file
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template PDF not found: {template_path}")
        
        self.pdf = pikepdf.open(str(template_path))
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
    
    def replace_text_in_content(
        self, 
        content: str, 
        replacements: Dict[str, str]
    ) -> str:
        """
        Replace text in PDF content stream using CID mappings.
        Handles both simple sequences and sequences with spacing adjustments.
        
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
                
                if old_cid_hex and new_cid_hex:
                    # Try exact replacement first (for simple cases like IDs)
                    if old_cid_hex in result:
                        count = result.count(old_cid_hex)
                        result = result.replace(old_cid_hex, new_cid_hex)
                        if count > 0:
                            print(f"    Replaced ({font_name}): {old_text} → {new_text} ({count} occurrences)")
                    
                    # For Japanese text, also try pattern with spacing adjustments
                    # Pattern: <XXXX>NUMBER<YYYY>NUMBER<ZZZZ>...
                    # We need to replace each <code> part and preserve the spacing
                    import re
                    
                    # Build pattern for old text with any spacing between codes
                    old_codes = re.findall(r'<([0-9A-Fa-f]+)>', old_cid_hex)
                    new_codes = re.findall(r'<([0-9A-Fa-f]+)>', new_cid_hex)
                    
                    if old_codes and new_codes:
                        # Build a regex pattern that matches the old codes with spacing
                        # e.g., <1EE4>-?[0-9.]*<388C>-?[0-9.]*<13D5>-?[0-9.]*<0B85>
                        pattern = r'<' + old_codes[0] + r'>(?:-?[0-9.]+)?'
                        for code in old_codes[1:]:
                            pattern += r'<' + code + r'>(?:-?[0-9.]+)?'
                        
                        # Find matches
                        matches = list(re.finditer(pattern, result))
                        if matches:
                            # Replace from end to beginning to preserve positions
                            for match in reversed(matches):
                                old_match = match.group(0)
                                # Build replacement preserving spacing
                                new_match = ''
                                spacing_pattern = re.findall(r'(<[0-9A-Fa-f]+>)(-?[0-9.]*)', old_match)
                                for i, new_code in enumerate(new_codes):
                                    new_match += f'<{new_code}>'
                                    if i < len(spacing_pattern) and spacing_pattern[i][1]:
                                        new_match += spacing_pattern[i][1]
                                
                                result = result[:match.start()] + new_match + result[match.end():]
                            
                            print(f"    Replaced ({font_name}): {old_text} → {new_text} ({len(matches)} occurrences with spacing)")
        
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
        # Get the content and create a modified version
        content = self.get_content_stream(source_page_index)
        modified_content = self.replace_text_in_content(content, replacements)
        
        # Create a new content stream
        new_content_stream = pikepdf.Stream(source_pdf, modified_content.encode('latin-1'))
        
        # Append the page
        source_pdf.pages.append(source_pdf.pages[source_page_index])
        
        # Get the newly appended page and modify its content
        appended_page = source_pdf.pages[-1]
        appended_page.Contents = new_content_stream
    
    def generate_allowance_pdf(
        self,
        output_path: str,
        employees: List[Dict[str, str]],
        template_page_index: int = 0,
    ) -> None:
        """
        Generate an allowance test PDF with duplicated pages and employee data.
        
        Args:
            output_path: Path for output PDF
            employees: List of dicts with "employee_id" and "name" keys
            template_page_index: Which page to use as template
        """
        if not employees:
            raise ValueError("employees list cannot be empty")
        
        # Create output PDF starting from template
        output_pdf = pikepdf.open(str(self.template_path))
        
        # Normalize template page index
        if template_page_index < 0:
            template_page_index = len(self.pdf.pages) + template_page_index
        
        if template_page_index >= len(self.pdf.pages):
            raise ValueError(f"Template page {template_page_index} out of range")
        
        print(f"\nProcessing {len(employees)} employees...")
        print(f"Using template page {template_page_index}")
        
        # Template has about 31 rows per page
        rows_per_page = 31
        
        # Calculate how many pages we need
        pages_needed = (len(employees) + rows_per_page - 1) // rows_per_page
        print(f"Rows per page: {rows_per_page}")
        print(f"Pages needed: {pages_needed}")
        
        # Create pages and fill them with employees
        employee_index = 0
        for page_num in range(pages_needed):
            print(f"\n  Page {page_num + 1}:")
            
            # Build replacements for this page
            replacements = {}
            
            # For each row on the template, assign the next employee
            for row_index in range(rows_per_page):
                if employee_index >= len(employees):
                    break
                
                employee = employees[employee_index]
                employee_id = employee.get("employee_id", "").strip()
                name = employee.get("name", "").strip()
                
                if not employee_id or not name:
                    employee_index += 1
                    continue
                
                # Get the template employee for this row
                template_emp = self.DEFAULT_EMPLOYEES[row_index % len(self.DEFAULT_EMPLOYEES)]
                
                # Replace this template employee's data with the current employee's data
                replacements[template_emp["employee_id"]] = employee_id
                template_name_no_space = template_emp["name"].replace(" ", "")
                new_name_no_space = name.replace(" ", "")
                replacements[template_name_no_space] = new_name_no_space
                
                print(f"    Row {row_index + 1}: {name} (ID: {employee_id})")
                employee_index += 1
            
            # Create the page with all replacements for this page
            if replacements:
                self.create_page_with_replacements(
                    output_pdf,
                    template_page_index,
                    replacements
                )
        
        # Remove the original template pages (keep only the generated ones)
        # The template has 2 pages, so we remove the first template_page_index + 1 pages
        # and keep all the duplicated pages we added
        original_page_count = len(self.pdf.pages)
        
        # Delete original pages from the output PDF
        # Since we appended pages, the original pages are at the beginning
        for _ in range(original_page_count):
            del output_pdf.pages[0]
        
        # Save output
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_pdf.save(output_path)
        
        print(f"\n✓ Generated allowance PDF: {output_path}")
        print(f"  Total pages: {len(output_pdf.pages)} (only modified pages, originals excluded)")
        print(f"  Template page used: {template_page_index}")
    
    def close(self) -> None:
        """Close the PDF."""
        self.pdf.close()


def load_employees_from_json(json_path: str) -> List[Dict[str, str]]:
    """
    Load employee data from a JSON file.
    
    Expected format:
    [
        {"employee_id": "123456", "name": "田中 太郎"},
        {"employee_id": "123457", "name": "佐藤 花子"},
        ...
    ]
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        List of employee dictionaries
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON must contain an array of employee objects")
        
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")


def main():
    """Main entry point with CLI support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate driver allowance test PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate PDF with default 40 employees
  python gen_allowance.py
  
  # Generate PDF with 20 employees
  python gen_allowance.py -n 20
  
  # Generate PDF with employees from JSON file
  python gen_allowance.py -f employees.json
  
  # Generate PDF with specific output path
  python gen_allowance.py -o custom_output.pdf
  
  # Generate PDF with 30 employees and custom output
  python gen_allowance.py -n 30 -o output/allowance_30.pdf
        """
    )
    
    parser.add_argument(
        '-n', '--num-employees',
        type=int,
        default=40,
        help='Number of employees to generate (default: 40)'
    )
    parser.add_argument(
        '-f', '--from-json',
        type=str,
        default=None,
        help='Load employee data from JSON file (default: materials/attendance300.json if it exists)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output/allowance_test.pdf',
        help='Output PDF path (default: output/allowance_test.pdf)'
    )
    parser.add_argument(
        '-t', '--template',
        type=str,
        default='materials/運転手手当一覧表 - Untenshu teate ichiran hyō - Driver Allowance List.pdf',
        help='Template PDF path'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Driver Allowance PDF Test Data Generator")
    print("=" * 60)
    
    try:
        # Load employee data
        # Priority: explicit -f flag, then materials/attendance300.json, then default list
        if args.from_json:
            print(f"\nLoading employees from: {args.from_json}")
            employees = load_employees_from_json(args.from_json)
            print(f"Loaded {len(employees)} employees from JSON")
        elif Path('materials/attendance300.json').exists():
            print(f"\nLoading employees from: materials/attendance300.json")
            employees = load_employees_from_json('materials/attendance300.json')
            print(f"Loaded {len(employees)} employees from JSON")
        else:
            employees = AllowancePDFGenerator.DEFAULT_EMPLOYEES[:args.num_employees]
            print(f"\nUsing default employee list")
            print(f"Generating {len(employees)} employees")
        
        # Limit to specified number of employees
        if len(employees) > args.num_employees:
            employees = employees[:args.num_employees]
            print(f"Limited to first {args.num_employees} employees")
        
        # Initialize generator
        print(f"\nTemplate: {args.template}")
        generator = AllowancePDFGenerator(args.template)
        print(f"✓ Loaded template with {generator.total_pages} pages")
        print(f"✓ Extracted font mappings for {len(generator.font_mappings)} fonts")
        
        # Generate PDF
        generator.generate_allowance_pdf(
            output_path=args.output,
            employees=employees,
            template_page_index=0
        )
        
        generator.close()
        
        print("\n" + "=" * 60)
        print("✓ PDF generation complete!")
        print("=" * 60)
        print(f"\nOutput file: {args.output}")
        print("\nYou can now use Camelot to extract and verify the table data:")
        print(f"  python -m camelot.cli extract -o output/extracted/ {args.output}")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
