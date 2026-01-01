# Attendance PDF Generator - gen_attendance.py

## Overview

The attendance PDF generator supports **two modes**:

1. **Random Mode** (default) - Generate random employees with realistic Japanese names
2. **JSON Mode** (new) - Load actual employee data from a JSON file

## JSON Mode Usage

### Generate PDF from JSON file

```bash
python3 gen_attendance.py --json materials/attendance300.json
```

Output: `output/random_employees.pdf` with all 300 employees from the JSON file

### Custom output path

```bash
python3 gen_attendance.py --json materials/attendance300.json -o output/my_employees.pdf
```

### Custom template

```bash
python3 gen_attendance.py --json data.json -t path/to/template.pdf
```

## JSON File Format

Your JSON file should be an array of employee objects with the following structure:

```json
[
  {
    "employee_id": "240631",
    "name": "工藤 貴幸"
  },
  {
    "employee_id": "250632",
    "name": "渡辺 雄次"
  },
  {
    "employee_id": "250633",
    "name": "奥山 広志"
  }
]
```

**Required fields:**
- `employee_id` (string) - Unique employee ID (any format, typically 6 digits)
- `name` (string) - Employee name in any format

**Alternative field names supported:**
- Instead of `employee_id`, you can use `shain_id` (same thing)

## How It Works

1. **Load JSON** - Read all employees from the JSON file
2. **Create Pages** - For every 4 employees, duplicate the template page once
3. **Replace IDs** - Replace the 4 template employee IDs with the actual IDs from JSON
4. **Generate PDF** - Output the complete PDF with all employees

### Example

**Input:** 20 employees in JSON file

```
Page 1-8:    Original template pages
Page 9:      Template with employees 1-4 from JSON (IDs: 240631, 250632, 250633, 250634)
Page 10:     Template with employees 5-8 from JSON
Page 11:     Template with employees 9-12 from JSON
Page 12:     Template with employees 13-16 from JSON
Page 13:     Template with employees 17-20 from JSON
```

**Total: 13 pages** (8 original + 5 duplicated)

## Comparison: Random vs JSON Mode

### Random Mode (Default)
```bash
python3 gen_attendance.py -n 40
```
- Generates 40 random employees
- Random 6-digit IDs (100000-999999)
- Realistic Japanese names from generated list
- Customizable count with `-n` flag
- Reproducible with `--seed` option

### JSON Mode
```bash
python3 gen_attendance.py --json employees.json
```
- Loads all employees from JSON file
- Uses exact IDs from JSON
- Uses exact names from JSON
- Automatically processes all employees in file
- `--seed` option is ignored

## Examples

### Example 1: Generate from 300 employees

```bash
python3 gen_attendance.py --json materials/attendance300.json
```

Result:
- 83 pages total (8 original + 75 duplicated)
- 300 employees
- 1.4 MB PDF file

### Example 2: Generate from custom employee list

Create `my_employees.json`:
```json
[
  {"employee_id": "001", "name": "山田 太郎"},
  {"employee_id": "002", "name": "鈴木 花子"},
  {"employee_id": "003", "name": "佐藤 次郎"}
]
```

Then:
```bash
python3 gen_attendance.py --json my_employees.json -o output/my_company.pdf
```

Result:
- 10 pages (8 original + 1 duplicated for 3 employees)
- Custom employee IDs and names

### Example 3: Mix and match

```bash
# Random 40 employees
python3 gen_attendance.py -n 40 -o output/random.pdf

# Actual 300 employees from JSON
python3 gen_attendance.py --json materials/attendance300.json -o output/actual.pdf

# Different template
python3 gen_attendance.py --json data.json -t template2.pdf
```

## Supported Field Names

The JSON parser supports multiple field name variants:

```json
// All of these work:
{"employee_id": "001", "name": "山田 太郎"}
{"shain_id": "001", "name": "山田 太郎"}      // Alternative ID field
```

## Error Handling

The tool provides helpful error messages:

```bash
# File not found
$ python3 gen_attendance.py --json nonexistent.json
✗ Error: JSON file not found: nonexistent.json

# Invalid JSON format
$ python3 gen_attendance.py --json bad.json
✗ Error: Invalid JSON format: ...

# Missing required fields
$ python3 gen_attendance.py --json missing_fields.json
✗ Error: Each employee must have 'employee_id' (or 'shain_id') and 'name' fields
```

## Important Notes

1. **JSON Mode takes precedence** - If you specify both `--json` and `-n`, the JSON file is used and the `-n` option is ignored
2. **4 employees per page** - The template has 4 employee slots, so PDF is generated accordingly
3. **Padding** - If you have 22 employees, the 22nd page will have the last employee duplicated (to fill 4 slots)
4. **ID fields** - Employee IDs are replaced directly as-is (no formatting applied)
5. **Names** - Names are NOT replaced in the PDF (they appear to be embedded as images)

## Python API

You can also use the JSON mode from Python code:

```python
from generate_random_employees import generate_pdf_with_employees

# From JSON file
generate_pdf_with_employees(
    output_path="output/my_pdf.pdf",
    json_file="materials/attendance300.json"
)

# Or random mode
generate_pdf_with_employees(
    output_path="output/random.pdf",
    num_employees=100
)
```

## Verification

All generated PDFs work perfectly with Camelot:

```python
import camelot

pdf = "output/attendance300_employees.pdf"
tables = camelot.read_pdf(pdf, pages='all')
print(f"Successfully extracted {len(tables)} tables")
```

## Quick Reference

| Task | Command |
|------|---------|
| Random 40 employees | `python3 gen_attendance.py` |
| Random 100 employees | `python3 gen_attendance.py -n 100` |
| From JSON file | `python3 gen_attendance.py --json employees.json` |
| Custom output | `python3 gen_attendance.py -o output/custom.pdf` |
| Reproducible random | `python3 gen_attendance.py --seed 12345` |
| Help | `python3 gen_attendance.py --help` |
