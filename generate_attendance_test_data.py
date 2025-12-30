"""
Generate a PDF with customizable attendance book test data.
Creates pages with 4 employees each, with unique IDs and names.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json


class AttendanceTestDataGenerator:
    """Generate attendance book test data PDF."""
    
    def __init__(self, num_employees=300):
        """
        Initialize the generator.
        
        Args:
            num_employees (int): Total number of employees to generate
        """
        self.num_employees = num_employees
        self.base_data = [
            {"id": 240631, "name": "工藤 貴幸"},
            {"id": 250632, "name": "渡辺 雄次"},
            {"id": 250633, "name": "奥山 広志"},
            {"id": 250634, "name": "安井 直樹"},
        ]
        self.employees = []
        self._generate_employees()
    
    def _generate_employees(self):
        """Generate unique employee data based on base data."""
        generated = set()
        self.employees = []
        
        # Start with base employees
        for emp in self.base_data:
            self.employees.append({
                "shain_id": str(emp["id"]),
                "shimei": emp["name"]
            })
            generated.add(emp["id"])
        
        # Generate additional employees if needed
        current_id = 250635
        base_names = [emp["name"].split()[1] for emp in self.base_data]  # Extract family names
        
        while len(self.employees) < self.num_employees:
            # Create unique ID
            while current_id in generated:
                current_id += 1
            
            # Generate name by cycling through base names and adding variation
            name_idx = (len(self.employees) - len(self.base_data)) % len(base_names)
            base_name = base_names[name_idx]
            count = (len(self.employees) - len(self.base_data)) // len(base_names)
            
            # Create varied name
            if count == 0:
                generated_name = base_name
            else:
                # Add variation using different patterns
                variations = ["太郎", "次郎", "三郎", "四郎", "五郎", "六郎", "七郎", "八郎", "九郎"]
                var_name = variations[count % len(variations)]
                generated_name = f"{base_name} {var_name}"
            
            self.employees.append({
                "shain_id": str(current_id),
                "shimei": generated_name
            })
            generated.add(current_id)
            current_id += 1
    
    def _create_employee_table(self, employees_list):
        """
        Create a table for 4 employees on a page.
        
        Args:
            employees_list (list): List of 4 employees
            
        Returns:
            Table: ReportLab Table object
        """
        # Header row
        data = [
            ["社員ID", "氏名", "社員ID", "氏名"],
        ]
        
        # Add 2 rows of 2 employees each
        for i in range(0, 4, 2):
            if i + 1 < len(employees_list):
                row = [
                    employees_list[i]["shain_id"],
                    employees_list[i]["shimei"],
                    employees_list[i + 1]["shain_id"],
                    employees_list[i + 1]["shimei"],
                ]
            else:
                row = [
                    employees_list[i]["shain_id"],
                    employees_list[i]["shimei"],
                    "",
                    "",
                ]
            data.append(row)
        
        # Create table
        table = Table(data, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 50),
        ]))
        
        return table
    
    def generate_pdf(self, output_path=None):
        """
        Generate the PDF file.
        
        Args:
            output_path (str): Output file path. Defaults to output/attendance_testdata.pdf
        """
        if output_path is None:
            output_path = "output/attendance_testdata.pdf"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=10*mm,
            leftMargin=10*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
        )
        
        # Build content
        story = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        
        story.append(Paragraph(f"出勤簿 - テストデータ ({self.num_employees}名)", title_style))
        story.append(Spacer(1, 10*mm))
        
        # Add pages with 4 employees each
        for page_num in range(0, self.num_employees, 4):
            if page_num > 0 and page_num % 4 == 0:
                story.append(PageBreak())
            
            # Get 4 employees for this page (or less if at the end)
            page_employees = self.employees[page_num:min(page_num + 4, self.num_employees)]
            
            # Add page title
            page_style = ParagraphStyle(
                'PageTitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=10,
            )
            story.append(Paragraph(
                f"ページ {page_num // 4 + 1} ({page_num + 1}-{min(page_num + 4, self.num_employees)}番目)",
                page_style
            ))
            
            # Add table
            table = self._create_employee_table(page_employees)
            story.append(table)
            story.append(Spacer(1, 15*mm))
        
        # Build PDF
        doc.build(story)
        print(f"✓ PDF generated: {output_path}")
        print(f"  Total employees: {self.num_employees}")
        print(f"  Total pages: {(self.num_employees + 3) // 4}")
    
    def save_json(self, output_path=None):
        """
        Save employee data as JSON for reference.
        
        Args:
            output_path (str): Output file path. Defaults to output/attendance_testdata.json
        """
        if output_path is None:
            output_path = "output/attendance_testdata.json"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.employees, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON data saved: {output_path}")


# Define cm for easier reference
cm = 28.346


def main():
    """Main function to generate test data."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate attendance book test data PDF"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=300,
        help="Number of employees to generate (default: 300)"
    )
    parser.add_argument(
        "--pdf-output",
        default="output/attendance_testdata.pdf",
        help="Output PDF file path"
    )
    parser.add_argument(
        "--json-output",
        default="output/attendance_testdata.json",
        help="Output JSON file path (for reference)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only generate JSON, skip PDF"
    )
    
    args = parser.parse_args()
    
    print(f"Generating test data for {args.employees} employees...")
    generator = AttendanceTestDataGenerator(num_employees=args.employees)
    
    if not args.json_only:
        generator.generate_pdf(args.pdf_output)
    generator.save_json(args.json_output)
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
