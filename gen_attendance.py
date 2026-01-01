#!/usr/bin/env python3
"""
Random Employee PDF Generator

Generates test PDFs with employee names and IDs.
- Creates 4 employees per page (duplicates the last page for each 4 employees)
- Can generate random 6-digit employee IDs with realistic Japanese names
- Or read from a JSON file with actual employee data
- Customizable number of employees (or pages)
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Tuple

from generate_test_pdf import PDFTestDataGenerator


# Common Japanese surnames
SURNAMES = [
    "田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤", "中村", "小林", "加藤", "吉田",
    "山田", "佐々木", "山本", "松田", "岡田", "山崎", "石田", "中島", "上田", "鈴木",
    "松本", "橋本", "村上", "山下", "阿部", "稲垣", "岩田", "植田", "馬場", "畑",
    "星野", "長谷川", "中田", "矢野", "大塚", "芝田", "成田", "長野", "三浦", "水野",
    "永田", "藤田", "梅田", "出口", "早川", "福田", "馬渕", "丸山", "松原", "右京",
    "岩村", "内田", "倉田", "倉持", "日高", "清水", "平田", "平野", "広瀬", "樋口",
    "福間", "船越", "古川", "保坂", "星", "本多", "本田", "牧野", "町田", "町村",
    "窓口", "丸田", "満田", "三上", "三村", "南", "みよし", "宮田", "宮本", "宮脇",
]

# Common Japanese given names (male and female mixed)
GIVEN_NAMES = [
    "太郎", "次郎", "三郎", "四郎", "五郎",
    "健太", "健二", "健三", "健四", "健五",
    "一郎", "二郎", "三郎", "四郎", "五郎",
    "佳幸", "直樹", "雄次", "広志", "貴幸",
    "信也", "拓也", "敏也", "聡也", "勝也",
    "春彦", "夏彦", "秋彦", "冬彦", "正彦",
    "花子", "美咲", "由美", "由梨", "美優",
    "智代", "知香", "千鶴", "茅野", "和美",
    "翼", "勇気", "聖", "翔", "駿",
    "康平", "陸平", "龍平", "流平", "琉平",
    "篤", "厚", "集", "淳", "潤",
    "瞬", "瞭", "瑞", "瑛", "瑠",
    "優", "祐", "悠", "雄", "勇",
    "亮", "量", "遼", "明", "晃",
    "章", "彰", "昭", "省", "翔",
]


def generate_random_id() -> str:
    """Generate a random 6-digit employee ID."""
    return str(random.randint(100000, 999999))


def generate_random_name() -> str:
    """Generate a random Japanese name (surname + given name)."""
    surname = random.choice(SURNAMES)
    given_name = random.choice(GIVEN_NAMES)
    return f"{surname} {given_name}"


def load_employees_from_json(json_path: str) -> List[Tuple[str, str]]:
    """
    Load employee data from a JSON file.
    
    Expected JSON format:
    [
        {"employee_id": "240631", "name": "工藤 貴幸"},
        {"employee_id": "250632", "name": "渡辺 雄次"},
        ...
    ]
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        List of (employee_id, employee_name) tuples
        
    Raises:
        FileNotFoundError: If JSON file not found
        ValueError: If JSON format is invalid
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    
    if not isinstance(data, list):
        raise ValueError("JSON must be an array of employee objects")
    
    employees = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each item in JSON array must be an object")
        
        # Support both 'employee_id' and 'shain_id' as ID key
        emp_id = item.get('employee_id') or item.get('shain_id')
        emp_name = item.get('name')
        
        if not emp_id or not emp_name:
            raise ValueError("Each employee must have 'employee_id' (or 'shain_id') and 'name' fields")
        
        employees.append((str(emp_id), str(emp_name)))
    
    if not employees:
        raise ValueError("JSON file contains no employees")
    
    return employees


def generate_random_employees(count: int = 40) -> List[Tuple[str, str]]:
    """
    Generate random employees with unique IDs.
    
    Args:
        count: Number of employees to generate
        
    Returns:
        List of (employee_id, employee_name) tuples
    """
    employees = []
    used_ids = set()
    
    for _ in range(count):
        # Generate unique ID
        while True:
            emp_id = generate_random_id()
            if emp_id not in used_ids:
                used_ids.add(emp_id)
                break
        
        emp_name = generate_random_name()
        employees.append((emp_id, emp_name))
    
    return employees


def generate_pdf_with_employees(
    output_path: str = "output/random_employees.pdf",
    num_employees: int = None,
    json_file: str = None,
    template_path: str = "materials/出勤簿 - shukkinbo - attendance book.pdf",
    generated_only: bool = False
) -> None:
    """
    Generate a PDF with employees from random generation or JSON file.
    
    Args:
        output_path: Path for output PDF
        num_employees: Number of random employees to generate (ignored if json_file provided)
        json_file: Path to JSON file with employee data
        template_path: Path to template PDF
        generated_only: If True, only include duplicated pages (exclude original 8 pages)
    """
    print("="*70)
    print(f"Employee PDF Generator")
    print("="*70)
    
    # Load employees from JSON or generate random
    if json_file:
        print(f"\nLoading employees from JSON: {json_file}")
        try:
            employees = load_employees_from_json(json_file)
            num_employees = len(employees)
            print(f"Loaded {num_employees} employees from JSON file")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            print(f"\n✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Generate random employees
        if num_employees is None:
            num_employees = 40
        
        print(f"\nGenerating {num_employees} random employees...\n")
        employees = generate_random_employees(num_employees)
    
    # Print first 10 employees as preview
    print("Employees:")
    print("-" * 70)
    for i, (emp_id, emp_name) in enumerate(employees[:10]):
        print(f"  {i+1:3d}. {emp_id} - {emp_name}")
    if len(employees) > 10:
        print(f"  ... and {len(employees) - 10} more employees")
    print("-" * 70)
    
    # The template page has 4 employees with these IDs
    template_ids = ["240631", "250632", "250633", "250634"]
    
    # Create test_data entries
    # First entry keeps the original template (unless generated_only is True)
    if generated_only:
        test_data = []
    else:
        test_data = [{}]
    
    # Add replacement entries for each employee after the first
    # Each duplicated page replaces all 4 employees with a new set of 4 employees
    for i in range(0, len(employees), 4):
        # Get 4 employees (or remaining if less than 4 left)
        batch = employees[i:i+4]
        
        # Pad with duplicates if we have less than 4 employees
        while len(batch) < 4:
            batch.append(batch[0])
        
        # Create replacements for this batch
        replacements = {}
        for j, (template_id, (emp_id, emp_name)) in enumerate(zip(template_ids, batch)):
            replacements[template_id] = emp_id
        
        test_data.append(replacements)
    
    print(f"\nLoading template: {template_path}")
    print(f"Creating {len(test_data)} pages...\n")
    
    try:
        # Generate the PDF
        generator = PDFTestDataGenerator(template_path)
        
        generator.generate_test_pdf(
            output_path=output_path,
            test_data=test_data,
            template_page_index=-1,  # Use last page as template
            keep_original_first_page=not generated_only
        )
        
        generator.close()
        
        # Summary
        print("\n" + "="*70)
        print("✓ PDF Generation Complete!")
        print("="*70)
        print(f"\nOutput: {output_path}")
        print(f"Total Employees: {num_employees}")
        
        if generated_only:
            print(f"Total Pages: {len(test_data)}")  # Only generated pages
            print(f"Mode: Generated pages only (no original template pages)")
        else:
            print(f"Total Pages: {len(test_data) + 7}")  # Original 8 pages + new pages
            print(f"Mode: Original template pages + generated pages")
        
        print(f"File Size: {Path(output_path).stat().st_size / 1024:.1f} KB")
        print("\nYou can now use Camelot to extract employee data from the PDF!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def generate_pdf_with_random_employees(
    output_path: str = "output/random_employees.pdf",
    num_employees: int = 40,
    template_path: str = "materials/出勤簿 - shukkinbo - attendance book.pdf",
    generated_only: bool = False
) -> None:
    """
    Generate a PDF with random employees.
    
    Args:
        output_path: Path for output PDF
        num_employees: Number of employees to generate (default 40)
        template_path: Path to template PDF
        generated_only: If True, only include generated pages (exclude original 8 pages)
    """
    generate_pdf_with_employees(
        output_path=output_path,
        num_employees=num_employees,
        json_file=None,
        template_path=template_path,
        generated_only=generated_only
    )


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate test PDFs with employees from random generation or JSON file"
    )
    parser.add_argument(
        "-j", "--json",
        help="JSON file with employee data (employee_id and name fields)"
    )
    parser.add_argument(
        "-n", "--num-employees",
        type=int,
        default=40,
        help="Number of random employees to generate (ignored if --json provided, default: 40)"
    )
    parser.add_argument(
        "-o", "--output",
        default="output/random_employees.pdf",
        help="Output PDF path (default: output/random_employees.pdf)"
    )
    parser.add_argument(
        "-t", "--template",
        default="materials/出勤簿 - shukkinbo - attendance book.pdf",
        help="Template PDF path"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility (only used with random generation)"
    )
    parser.add_argument(
        "--generated-only",
        action="store_true",
        help="Only include generated pages (exclude original 8 template pages)"
    )
    
    args = parser.parse_args()
    
    # Set random seed if provided (only for random mode)
    if args.seed and not args.json:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}\n")
    
    # Generate PDF
    generate_pdf_with_employees(
        output_path=args.output,
        num_employees=args.num_employees if not args.json else None,
        json_file=args.json,
        template_path=args.template,
        generated_only=args.generated_only
    )


if __name__ == "__main__":
    main()
