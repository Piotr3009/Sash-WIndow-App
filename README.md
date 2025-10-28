# Sash Window App

Professional desktop application for designing and managing sash window production. Built with PyQt6 for a modern, cross-platform user interface.

## Features

- **Window Configuration**: Design sash windows with customizable dimensions, paint colors, hardware finishes, and glazing options
- **Automatic Calculations**: Calculates frame, sash, and glass dimensions based on manufacturing standards
- **Advanced Graphics & CAD System** 🎨:
  - Real-time 2D visualization with interactive viewer (pan, zoom, fit-to-window)
  - Professional CAD export to DXF format (compatible with AutoCAD, LibreCAD)
  - Scalable vector graphics (SVG) export for documentation
  - High-resolution PNG export with anti-aliasing
  - Proper layering system (FRAME, SASH, GLASS, BARS, DIMENSIONS)
  - Color-coded components with transparency support
  - Dimension lines with measurements in millimeters
- **Technical Drawings**: Generates detailed technical drawings with matplotlib
- **Material Cutting Lists**: Automatic generation of timber cutting lists and material specifications
- **Export Options**:
  - PDF reports with specifications, cutting lists, and shopping lists
  - Excel spreadsheets with detailed window data
  - DXF CAD files for manufacturing
  - SVG vector graphics for scalable documentation
  - PNG raster images for presentations
- **Database Integration**: Optional Supabase integration for project persistence
- **Professional UI**: Clean, intuitive tabbed interface with Graphics and Results views
- **Future-Ready Architecture**: Placeholder modules for 3D visualization (STL/OBJ), CNC G-code generation, and material nesting optimization

## Screenshots

The application provides:
- **Left panel**: Window configuration inputs with all design parameters
- **Graphics tab**: Interactive 2D viewer with pan/zoom controls and CAD export buttons (DXF, SVG, PNG)
- **Results tab**: Results preview, technical drawing, and log output
- **Export buttons**: PDF, Excel, DXF, SVG, and PNG generation

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
- **`output/` directory**: Legacy exports (PDF, Excel, matplotlib drawings)
  - `{project_name}_report.pdf` - Full specification report
  - `{project_name}_report.xlsx` - Detailed Excel workbook
  - `{window_name}_drawing.png` - Technical drawing (matplotlib)

- **`output/graphics/` directory**: Professional CAD and graphics exports
  - `{window_name}_cad.dxf` - DXF CAD file (R2018 format, layered)
  - `{window_name}_vector.svg` - SVG scalable vector graphics
  - `{window_name}_preview.png` - High-resolution PNG (300 DPI)

## Project Structure

```
Sash-WIndow-App/
├── gui_app/
│   ├── backend/
│   │   ├── calculations.py    # Window dimension calculations
│   │   ├── database.py        # Supabase integration
│   │   ├── drawings.py        # Technical drawing generation (matplotlib)
│   │   ├── export_excel.py    # Excel export functionality
│   │   ├── export_pdf.py      # PDF report generation
│   │   ├── models.py          # Data models
│   │   └── main.py            # Backend demo script
│   ├── graphics/              # 🎨 NEW: Advanced Graphics & CAD System
│   │   ├── base_exporter.py   # Abstract base class for exporters
│   │   ├── renderer.py        # Core geometry and rendering logic
│   │   ├── viewer.py          # PyQt6 interactive graphics viewer
│   │   ├── export_dxf.py      # DXF CAD export (ezdxf)
│   │   ├── export_svg.py      # SVG vector export
│   │   ├── export_png.py      # PNG raster export
│   │   ├── export_3d.py       # Placeholder: STL/OBJ (future)
│   │   ├── export_gcode.py    # Placeholder: CNC G-code (future)
│   │   └── nesting.py         # Placeholder: Material optimization (future)
│   ├── resources/
│   │   ├── icons/             # Application icons
│   │   └── style.qss          # Qt stylesheet
│   ├── __init__.py
│   └── main_gui.py            # Main GUI application with Graphics tab
├── tests/                     # Test suite
│   └── graphics/              # Graphics module tests
│       └── test_renderer.py   # Renderer tests
├── docs/                      # Documentation
│   └── graphics/
│       └── preview/           # Example screenshots and exports
├── output/                    # Generated output files
│   └── graphics/              # CAD and graphics exports
├── main_gui.py                # Application entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern Python packaging
├── setup.sh / setup.bat      # Automated setup scripts
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Graphics System Usage

### Interactive Graphics Viewer

After calculating a window design, switch to the **Graphics** tab to access:

- **🔄 Refresh**: Regenerate graphics visualization
- **🔍 Fit**: Fit window to view
- **➕ Zoom In / ➖ Zoom Out**: Interactive zoom controls
- **Mouse wheel**: Zoom in/out
- **Click and drag**: Pan the view

### CAD Export Features

**DXF Export** (💾 Export DXF):
- Industry-standard CAD format
- Compatible with AutoCAD, LibreCAD, QCAD, and other CAD software
- Proper layering: FRAME, SASH_TOP, SASH_BOTTOM, GLASS, BARS, DIMENSIONS, TEXT
- Units: millimeters
- Line weights: 0.15-0.50mm
- DXF version: R2018
- Includes metadata block with project information

**SVG Export** (🖼 Export SVG):
- Scalable vector graphics format
- Perfect for documentation, web pages, and print materials
- Maintains full quality at any scale
- Embedded metadata
- Layer-based organization using SVG groups
- Arrow markers for dimension lines

**PNG Export** (📷 Export PNG):
- High-resolution raster images (default 300 DPI)
- Anti-aliased rendering for professional quality
- Suitable for presentations, reports, and print
- Customizable resolution and background color

### Graphics Color Scheme

The graphics system uses a professional color scheme:
- **Frame**: `#444444` (Dark gray)
- **Sash**: `#4A90E2` (Professional blue)
- **Glass**: `#A0C4FF` (Light blue, 40% transparency)
- **Bars**: `#AAAAAA` (Medium gray, dotted lines)
- **Dimensions**: `#FF6B6B` (Red for dimension lines and text)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run graphics tests only
pytest tests/graphics/

# Run with coverage
pytest --cov=gui_app --cov-report=term-missing
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
