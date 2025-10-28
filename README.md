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

The application uses a **scene-based architecture** for professional CAD exports:

1. **Build Scene**: Generate geometry from window data using `build_scene()`
2. **Export**: Convert scene to DXF, SVG, or other formats
3. **Threaded Execution**: Exports run in background threads (non-blocking GUI)

#### DXF Export (💾 Export DXF)

**Professional AutoCAD-compatible CAD files:**
- **Format**: DXF R2018 (Modelspace only)
- **Units**: Millimeters
- **Coordinate System**: Bottom-left origin (CAD standard)
- **Compatible with**: AutoCAD, LibreCAD, QCAD, DraftSight

**Exact Layer Specifications** (9 layers with AutoCAD Color Index):

| Layer | Description | Color Code | Lineweight | Linetype |
|-------|-------------|------------|------------|----------|
| FRAME | Window frame outline | 7 (White/Black) | 0.50mm | Continuous |
| SASH_TOP | Top sash outline | 3 (Green) | 0.35mm | Continuous |
| SASH_BOTTOM | Bottom sash outline | 5 (Blue) | 0.35mm | Continuous |
| GLASS | Glass panel outline | 4 (Cyan) | 0.18mm | Continuous |
| BARS_V | Vertical glazing bars | 1 (Red) | 0.25mm | Continuous |
| BARS_H | Horizontal glazing bars | 2 (Yellow) | 0.25mm | Continuous |
| DIMENSIONS | Dimension lines & text | 8 (Dark Gray) | 0.18mm | Continuous |
| CENTERLINES | Reference axes | 9 (Light Gray) | 0.18mm | DashDot |
| ANNOTATIONS | Metadata text | 6 (Magenta) | 0.25mm | Continuous |

**Dimension Standards** (ISO compliant):
- Text height: 3.5mm
- Text offset: 5mm from geometry
- Arrow style: Standard ISO arrows (3mm)
- Dimension targets:
  - Overall frame width & height
  - Glass area width & height
  - Bar spacing (annotated)

**Metadata** (included in ANNOTATIONS layer):
- Project name
- Window ID
- Client name
- Date
- Dimensions
- Paint color
- Hardware finish

#### SVG Export (🖼 Export SVG)

**Scalable vector graphics for documentation:**
- XML-based vector format
- Embedded metadata (title, description)
- Layer-based organization using SVG `<g>` groups
- Arrow markers for dimensions
- Professional color scheme with hex codes
- Perfect for web, documentation, print

**Optional Preview Rendering:**
- Auto-generates PNG preview (800px width, 150 DPI)
- Requires `cairosvg` library: `pip install cairosvg`
- Displayed in GUI after export
- Saved alongside SVG file

#### PNG Export (📷 Export PNG)

- High-resolution raster images (300 DPI)
- Anti-aliased rendering
- Customizable resolution and background color

### Usage Examples

#### Basic CAD Export (GUI)

1. Configure and calculate a window
2. Click **💾 Export DXF** or **🖼 Export SVG**
3. Export runs in background (non-blocking)
4. File saved to `output/cad/` directory
5. Preview auto-generated (SVG only, if cairosvg installed)

#### Programmatic Usage

```python
from gui_app.backend.calculations import assemble_window
from gui_app.graphics.scene import build_scene
from gui_app.graphics.export_dxf import DXFExporter
from gui_app.graphics.export_svg import SVGExporter

# 1. Create window
window = assemble_window(
    window_id="w1",
    name="Living Room",
    frame_width=1200,
    frame_height=1600,
    vertical_bars=2,
    horizontal_bars=2,
    paint_color="White",
    hardware_finish="Chrome"
)

# 2. Build scene
scene = build_scene(window, include_dimensions=True)

# 3. Export to DXF
dxf_exporter = DXFExporter(output_dir="output/cad")
dxf_path = dxf_exporter.export_from_scene(scene)
print(f"DXF saved: {dxf_path}")

# 4. Export to SVG
svg_exporter = SVGExporter(output_dir="output/cad")
svg_path = svg_exporter.export_from_scene(scene)
print(f"SVG saved: {svg_path}")

# 5. Generate preview (optional)
from gui_app.graphics.preview import render_preview_svg, is_preview_available

if is_preview_available():
    png_path = render_preview_svg(
        svg_path,
        "output/cad/preview.png",
        width=800,
        dpi=150
    )
    print(f"Preview: {png_path}")
```

### Dependencies for Graphics

**Core (Required):**
```bash
pip install PyQt6 ezdxf svgwrite matplotlib
```

**Optional (SVG Preview):**
```bash
pip install cairosvg
```

**System Requirements for cairosvg:**
- **Ubuntu/Debian**: `sudo apt-get install libcairo2`
- **macOS**: `brew install cairo`
- **Windows**: Download from https://www.cairographics.org/

### Output Directory Structure

```
output/
├── {project}_report.pdf          # PDF reports
├── {project}_report.xlsx         # Excel workbooks
├── {window}_drawing.png          # matplotlib drawings
├── cad/                          # CAD exports (NEW)
│   ├── {window}_cad.dxf         # DXF CAD files
│   ├── {window}_vector.svg      # SVG vector files
│   └── {window}_vector.png      # SVG previews (if cairosvg installed)
```

### Graphics Color Scheme (SVG/PNG)

The graphics system uses professional hex colors:
- **Frame**: `#2C2C2C` (Dark gray)
- **Sash Top/Bottom**: `#4A90E2` (Professional blue)
- **Glass**: `#A0C4FF` (Light blue)
- **Bars**: `#888888` (Medium gray)
- **Dimensions**: `#FF0000` (Red)
- **Centerlines**: `#00FF00` (Green)
- **Annotations**: `#000000` (Black)

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
