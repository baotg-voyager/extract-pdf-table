# PDF Data Extraction Tool

Extract employee attendance and allowance data from PDF files using Camelot.

## Tools

### 1. Attendance PDF Generator (`gen_attendance.py`)

Generate attendance PDF files with employee data from JSON files or with random employees.

**Quick Start:**
```bash
# Generate 40 random employees
python3 gen_attendance.py

# Generate from JSON file
python3 gen_attendance.py --json materials/attendance300.json

# Generated pages only (no original template)
python3 gen_attendance.py --json materials/attendance300.json --generated-only
```

See [docs/ATTENDANCE_GENERATION_GUIDE.md](docs/ATTENDANCE_GENERATION_GUIDE.md) for complete documentation.

### 2. Data Extraction (`app.py`)

Extract data from attendance and allowance PDFs.

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Navigate to project directory:**
   ```bash
   cd /workspaces/camelot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -c "import camelot; print('✓ Camelot installed')"
   python -c "import pandas; print('✓ Pandas installed')"
   ```

## Usage

### Extract Attendance Data

```bash
python app.py attendance
```

Output: `output/attendance/attendance_records.{json,csv,md}`

### Extract Allowance Data

```bash
python app.py allowance
```

Output: `output/allowance/allowance_records.{json,csv,md}`

### Test Attendance Extraction

```bash
python app.py attendance --test
```

Compares against expected output. Expected: `✅ ALL TESTS PASSED!`

## How It Works

### Attendance
```
PDF → Camelot (lattice) → Find employees → Extract column 6 → JSON
```
- 8 tables × 4 employees = 32 records
- Salary fields in column 6

### Allowance
```
PDF → Camelot (stream) → Find employee rows → Map 37 columns → JSON
```
- Single table, 32 employees

## Project Structure

```
camelot/
├── app.py                 # Entry point
├── requirements.txt       # Dependencies
├── src/
│   ├── attendance/        # Attendance extraction
│   │   ├── parser.py      # Main parser entry point
│   │   ├── extract.py     # Data extraction functions
│   │   ├── helpers/       # Helper modules (refactored)
│   │   │   ├── __init__.py
│   │   │   ├── validation.py    # PDF validation
│   │   │   ├── table.py         # Table processing
│   │   │   ├── employee.py      # Employee record building
│   │   │   ├── extraction.py    # Data extraction utilities
│   │   │   └── utils.py         # Common utility functions
│   │   └── transformers.py  # Data transformation
│   ├── allowance/         # Allowance extraction
│   │   └── parser.py
│   └── common.py          # Shared functions
├── materials/             # Input PDFs
├── output/                # Generated files
└── docs/                  # Documentation
```

## Output Files

Generated in `output/` directory:

```
output/
├── attendance/
│   ├── attendance_records.json
│   ├── attendance_records.csv
│   └── attendance_records.md
└── allowance/
    ├── allowance_records.json
    ├── allowance_records.csv
    └── allowance_records.md
```

## Documentation

- [ATTENDANCE_EXTRACTION.md](docs/ATTENDANCE_EXTRACTION.md) - How extraction works
- [ATTENDANCE_FIELDS.md](docs/ATTENDANCE_FIELDS.md) - Field definitions
- [ALLOWANCE_EXTRACTION.md](docs/ALLOWANCE_EXTRACTION.md) - Allowance extraction details
- [ALLOWANCE_FIELDS.md](docs/ALLOWANCE_FIELDS.md) - Allowance field reference

## Troubleshooting

### ImportError: No module named 'camelot'

Install dependencies:
```bash
pip install -r requirements.txt
```

### PDF file not found

Ensure PDF is in `materials/` directory or use custom path:
```bash
python app.py attendance /path/to/file.pdf
```

### Permission denied

```bash
chmod +x app.py
```
