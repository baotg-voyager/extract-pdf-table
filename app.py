"""
PDF Parser Application
Execute: python app.py [attendance|allowance] [optional_pdf_path]
Test: python app.py [attendance|allowance] --test
"""

import sys
import json
import time
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python app.py [attendance|allowance] [optional_pdf_path|--test]")
        print("\nExamples:")
        print("  python app.py attendance")
        print("  python app.py allowance")
        print("  python app.py attendance --test")
        print("  python app.py allowance --test")
        print("  python app.py attendance /path/to/custom.pdf")
        print("  python app.py allowance /path/to/custom.pdf")
        sys.exit(1)
    
    parser_type = sys.argv[1].lower()
    test_mode = len(sys.argv) > 2 and sys.argv[2] == '--test'
    custom_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '--test' else None
    
    # Test mode
    if test_mode:
        if parser_type == "attendance":
            from src.attendance.test import test
            success = test()
        elif parser_type == "allowance":
            from src.allowance.test import test
            success = test()
        else:
            print(f"Unknown parser type: {parser_type}")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    # Normal extraction mode
    if parser_type == "attendance":
        print("\n" + "=" * 70)
        print("Running Attendance Parser...")
        print("=" * 70 + "\n")
        
        from src.attendance.parser import parse_pdf
        from src.common import save_json, save_csv, save_markdown
        
        pdf_path = custom_path or 'materials/出勤簿 - shukkinbo - attendance book.pdf'
        output_folder = 'output/attendance'
        
        print(f"PDF: {pdf_path}")
        print("=" * 70)
        
        # Measure parsing time
        parse_start = time.time()
        records = parse_pdf(pdf_path)
        parse_time = time.time() - parse_start
        
        # Measure processing time
        process_start = time.time()
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        save_json(records, f'{output_folder}/attendance_records.json')
        save_csv(records, f'{output_folder}/attendance_records.csv')
        save_markdown(records, f'{output_folder}/attendance_records.md', 'Attendance Records')
        
        process_time = time.time() - process_start
        
        print("\n" + "=" * 70)
        print(f"Extracted {len(records)} employee records")
        print("=" * 70)
        
        print("\n" + "=" * 70)
        print("TIMING RESULTS")
        print("=" * 70)
        print(f"Parsing time: {parse_time:.2f} seconds")
        print(f"Processing time: {process_time:.2f} seconds")
    
    elif parser_type == "allowance":
        print("\n" + "=" * 70)
        print("Running Allowance Parser...")
        print("=" * 70 + "\n")
        
        from src.allowance.parser import parse_pdf
        from src.common import save_json, save_csv, save_markdown
        
        pdf_path = custom_path or "materials/運転手手当一覧表 - Untenshu teate ichiran hyō - Driver Allowance List.pdf"
        output_folder = 'output/allowance'
        
        print(f"PDF: {pdf_path}")
        print("=" * 70)
        
        # Measure parsing time
        parse_start = time.time()
        employees = parse_pdf(pdf_path)
        parse_time = time.time() - parse_start
        
        if employees:
            # Measure processing time
            process_start = time.time()
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            save_json(employees, f'{output_folder}/driver_allowance.json')
            save_csv(employees, f'{output_folder}/driver_allowance.csv')
            save_markdown(employees, f'{output_folder}/driver_allowance.md', 'Driver Allowance List')
            
            process_time = time.time() - process_start
            
            print("\n" + "=" * 70)
            print(f"✓ Complete! {len(employees)} records → {output_folder}/")
            print("=" * 70)
            
            print("\n" + "=" * 70)
            print("TIMING RESULTS")
            print("=" * 70)
            print(f"Parsing time: {parse_time:.2f} seconds")
            print(f"Processing time: {process_time:.2f} seconds")
        print("Valid options: attendance, allowance")
        sys.exit(1)


if __name__ == "__main__":
    main()
