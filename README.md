# Sash Window App

Professional desktop application for designing and managing sash window production. Built with PyQt6 for a modern, cross-platform user interface.

## Features

- **Window Configuration**: Design sash windows with customizable dimensions, paint colors, hardware finishes, and glazing options
- **Automatic Calculations**: Calculates frame, sash, and glass dimensions based on manufacturing standards
- **Technical Drawings**: Generates detailed technical drawings with matplotlib
- **Material Cutting Lists**: Automatic generation of timber cutting lists and material specifications
- **Export Options**:
  - PDF reports with specifications, cutting lists, and shopping lists
  - Excel spreadsheets with detailed window data
- **Database Integration**: Optional Supabase integration for project persistence
- **Professional UI**: Clean, intuitive interface with real-time preview

## Screenshots

The application provides:
- Left panel: Window configuration inputs
- Right panel: Results preview, technical drawing, and log output
- Export buttons for PDF and Excel generation

## Requirements

- Python 3.10 or higher
- Operating System: Windows, macOS, or Linux

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Piotr3009/Sash-WIndow-App.git
cd Sash-WIndow-App
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or, for development with testing tools:

```bash
pip install -e ".[dev]"
```

### 4. Configure Environment (Optional)

For Supabase database integration:

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

If you don't configure Supabase, the application will run in offline mode (database features will be skipped).

## Usage

### Running the Application

```bash
python main_gui.py
```

Or, if installed with setuptools:

```bash
sash-window-app
```

### Using the Application

1. **Enter Project Details**:
   - Project Name
   - Client Name

2. **Configure Window Dimensions**:
   - Frame Width (400-4000mm)
   - Frame Height (400-4000mm)

3. **Select Options**:
   - Paint Color
   - Hardware Finish
   - Trickle Vent Type
   - Sash Catches
   - Cill Extension
   - Glazing Bars Layout

4. **Calculate**: Click "Calculate" to generate window specifications

5. **Export**:
   - Click "Generate PDF" for a comprehensive report
   - Click "Export Excel" for detailed spreadsheet

### Output Files

Generated files are saved in the `output/` directory:
- `{project_name}_report.pdf` - Full specification report
- `{project_name}_report.xlsx` - Detailed Excel workbook
- `{window_name}_drawing.png` - Technical drawing

## Project Structure

```
Sash-WIndow-App/
├── gui_app/
│   ├── backend/
│   │   ├── calculations.py    # Window dimension calculations
│   │   ├── database.py        # Supabase integration
│   │   ├── drawings.py        # Technical drawing generation
│   │   ├── export_excel.py    # Excel export functionality
│   │   ├── export_pdf.py      # PDF report generation
│   │   ├── models.py          # Data models
│   │   └── main.py            # Backend demo script
│   ├── resources/
│   │   ├── icons/             # Application icons
│   │   └── style.qss          # Qt stylesheet
│   ├── __init__.py
│   └── main_gui.py            # Main GUI application
├── main_gui.py                # Application entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern Python packaging
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The project uses modern Python development tools:

- **black**: Code formatting
- **ruff**: Fast Python linter
- **mypy**: Static type checking

Run code quality checks:

```bash
# Format code
black gui_app/

# Lint code
ruff check gui_app/

# Type checking
mypy gui_app/
```

## Manufacturing Standards

The application uses the following constants (in millimeters):

- Horn Allowance: 70mm
- Sash Width Deduction: 178mm
- Jambs Deduction: 106mm
- Glass Width Deduction: 90mm
- Glass Height Deduction: 76mm

These can be adjusted in `gui_app/backend/calculations.py` if needed.

## Database Schema (Supabase)

If using Supabase integration, create the following tables:

### projects
- id (uuid, primary key)
- name (text)
- client_name (text)
- created_at (timestamp)

### windows
- id (uuid, primary key)
- project_id (uuid, foreign key)
- name (text)
- frame_width (float)
- frame_height (float)
- paint_color (text)
- hardware_finish (text)
- trickle_vent (text)
- sash_catches (text)
- cill_extension (int)

### materials
- id (uuid, primary key)
- window_id (uuid, foreign key)
- material_type (text)
- section (text)
- length (float)
- qty (int)
- wood_type (text)

### glass
- id (uuid, primary key)
- window_id (uuid, foreign key)
- width (float)
- height (float)
- type (text)
- pcs (int)
- spacer_color (text)
- toughened (boolean)
- frosted (boolean)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/Piotr3009/Sash-WIndow-App/issues)

## Acknowledgments

- Built with PyQt6 for cross-platform GUI
- PDF generation powered by ReportLab
- Excel export using openpyxl
- Technical drawings with matplotlib
