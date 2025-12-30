"""
Generate attendance book test data by duplicating the last page with proper text replacement.
Uses PyMuPDF (fitz) with text search and redaction/reinsertion for reliable text replacement.
"""

import os
import json
import fitz  # PyMuPDF
from faker import Faker


class AttendanceTestDataGenerator:
    """Generate attendance book test data."""
    
    def __init__(self, template_pdf_path, num_employees=300):
        """Initialize the generator."""
        self.template_pdf_path = template_pdf_path
        self.num_employees = num_employees
        self.employees = []
        self._generate_employees()
    
    def _generate_employees(self):
        """Generate unique employee data."""
        fake = Faker('ja_JP')
        
        base_data = [
            {"id": 240631, "name": "工藤 貴幸"},
            {"id": 250632, "name": "渡辺 雄次"},
            {"id": 250633, "name": "奥山 広志"},
            {"id": 250634, "name": "安井 直樹"},
        ]
        
        generated = set()
        self.employees = []
        
        for emp in base_data:
            self.employees.append({
                "shain_id": str(emp["id"]),
                "shimei": emp["name"]
            })
            generated.add(emp["id"])
        
        current_id = 250635
        
        while len(self.employees) < self.num_employees:
            while current_id in generated:
                current_id += 1
            
            # Generate random Japanese name
            random_name = fake.name()
            
            self.employees.append({
                "shain_id": str(current_id),
                "shimei": random_name
            })
            generated.add(current_id)
            current_id += 1
    
    def generate_pdf(self, output_path=None):
        """Generate the PDF file by duplicating and replacing text."""
        if output_path is None:
            output_path = "output/attendance_testdata.pdf"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Open original PDF
        doc = fitz.open(self.template_pdf_path)
        template_page_idx = len(doc) - 1
        
        # Create output PDF
        output_doc = fitz.open()
        
        print(f"Generating {self.num_employees} employees ({(self.num_employees + 3) // 4} pages)...")
        
        # Original employee data
        original_employees = [
            ("240631", "工藤 貴幸"),
            ("250632", "渡辺 雄次"),
            ("250633", "奥山 広志"),
            ("250634", "安井 直樹"),
        ]
        
        # Generate pages
        for page_num in range(0, self.num_employees, 4):
            page_idx = page_num // 4
            
            # Get employees for this page
            page_employees = self.employees[page_num:min(page_num + 4, self.num_employees)]
            
            # Duplicate the template page
            output_doc.insert_pdf(doc, from_page=template_page_idx, to_page=template_page_idx)
            new_page = output_doc[-1]
            
            # Replace text for each employee
            for i, emp in enumerate(page_employees):
                if i < len(original_employees):
                    old_id, old_name = original_employees[i]
                    
                    # Find and replace ID
                    try:
                        for hit in new_page.search_for(old_id):
                            # Redact (white out) the old text
                            new_page.draw_rect(hit, color=None, fill=(1, 1, 1))
                            # Add the new text at the same position
                            new_page.insert_text((hit.x0, hit.y1), emp["shain_id"], fontsize=5.35, color=(0, 0, 0))
                    except:
                        pass
                    
                    # Find and replace name
                    try:
                        for hit in new_page.search_for(old_name):
                            # Redact the old text
                            new_page.draw_rect(hit, color=None, fill=(1, 1, 1))
                            # Add the new text
                            new_page.insert_text((hit.x0, hit.y1), emp["shimei"], fontsize=10, color=(0, 0, 0))
                    except:
                        pass
            
            if (page_idx + 1) % 10 == 0:
                print(f"  Created {page_idx + 1}/{(self.num_employees + 3) // 4} pages...")
        
        # Save output
        output_doc.save(output_path)
        output_doc.close()
        doc.close()
        
        print(f"✓ PDF generated: {output_path}")
    
    def save_json(self, output_path=None):
        """Save employee data as JSON."""
        if output_path is None:
            output_path = "output/attendance_testdata.json"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.employees, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON data saved: {output_path}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate attendance book test data PDF"
    )
    parser.add_argument(
        "--template",
        default="materials/出勤簿 - shukkinbo - attendance book.pdf",
        help="Template PDF file path"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=300,
        help="Number of employees (default: 300)"
    )
    parser.add_argument(
        "--pdf-output",
        default="output/attendance_testdata.pdf",
        help="Output PDF path"
    )
    parser.add_argument(
        "--json-output",
        default="output/attendance_testdata.json",
        help="Output JSON path"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only generate JSON"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.template):
        print(f"Error: Template not found: {args.template}")
        return 1
    
    print(f"Using template: {args.template}")
    print(f"Generating {args.employees} employees...\n")
    
    generator = AttendanceTestDataGenerator(
        template_pdf_path=args.template,
        num_employees=args.employees
    )
    
    if not args.json_only:
        generator.generate_pdf(args.pdf_output)
    generator.save_json(args.json_output)
    
    print("\n✓ Done!")
    return 0


if __name__ == "__main__":
    exit(main())
