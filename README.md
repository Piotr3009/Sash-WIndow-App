# Sash Window Designer - Backend System

**Skylon Elements – Sash Window Designer v1.0**

A complete, production-quality backend system for designing and calculating box sash windows. This system handles all component calculations, database storage, and export generation for professional sash window manufacturing.

## Features

- **Complete Window Calculations**: Automatically calculates all dimensions for frames, sashes, glass, and glazing bars
- **Database Integration**: Full Supabase (PostgreSQL) integration for project and window data
- **Multiple Export Formats**:
  - **Excel**: Detailed specifications and cutting lists
  - **PDF**: Professional A4 reports with specifications, cutting lists, shopping lists, and technical drawings
  - **PNG**: Technical drawings with dimensions and annotations
- **Modular Architecture**: Clean, extensible Python code ready for GUI integration
- **Production Ready**: Professional calculations following industry standards

## System Requirements

- Python 3.11 or higher
- Internet connection (for Supabase integration)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Sash-WIndow-App
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

## Quick Start

Run the demo program:

```bash
python main.py
```

This will:
1. Create a sample project with 3 windows
2. Calculate all dimensions
3. Save to Supabase (if configured)
4. Generate Excel, PDF, and PNG exports in the `output/` directory

## Project Structure

```
Sash-WIndow-App/
├── models.py           # Data models (Project, Window, Frame, Sash, Glass, Bars)
├── calculations.py     # Calculation engine with all formulas
├── database.py         # Supabase database interface
├── export_excel.py     # Excel report generation
├── export_pdf.py       # PDF report generation
├── drawings.py         # Technical drawing generation
├── main.py            # Demo application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── output/            # Generated files (created automatically)
```

## Module Documentation

### models.py
Defines all data structures:
- `Project`: Container for multiple windows
- `Window`: Complete window specification
- `Frame`: Frame dimensions
- `Sash`: Individual sash (top/bottom)
- `Glass`: Glass specifications
- `Bars`: Glazing bars configuration

### calculations.py
Implements all calculation formulas:
- Frame dimensions (jambs, head, cill, liners)
- Sash dimensions (width, height, horns)
- Glass dimensions
- Glazing bar spacing
- Cutting lists
- Shopping lists

**Key Formulas**:
- Sash Width = Frame Width - 178mm
- Sash Height with Horn = Sash Height + 70mm
- Jambs Length = Frame Height - 106mm
- Glass Width = Sash Width - 90mm
- Glass Height = Sash Height - 76mm

### database.py
Supabase integration with functions:
- `save_project()`: Save project and all windows
- `save_window()`: Save individual window
- `get_project()`: Retrieve project data
- `get_window()`: Retrieve window data

**Database Tables**:
- `projects`: Project metadata
- `windows`: Window specifications
- `materials`: Cutting list items
- `glass`: Glass specifications

### export_excel.py
Creates Excel workbooks with:
- Individual sheets per window
- Summary sheet with totals
- Formatted tables with headers
- Cutting lists and specifications

### export_pdf.py
Generates professional PDF reports with:
- **Page 1**: Window specifications
- **Page 2**: Cutting list with totals
- **Page 3**: Shopping list
- **Page 4**: Technical drawing
- Headers, footers, and page numbers

### drawings.py
Creates technical drawings with:
- Scaled frame and sash representations
- Glass areas
- Glazing bars (if configured)
- Dimension annotations
- Specifications summary

## Usage Examples

### Create a Custom Window

```python
from models import Project
from calculations import calculate_window
from database import save_project
from export_excel import create_excel_report
from export_pdf import create_pdf_report
from drawings import draw_window

# Create project
project = Project(
    name="My Project",
    client_name="Client Name"
)

# Calculate window
window = calculate_window(
    name="W-1",
    frame_width=1200,      # mm
    frame_height=1800,     # mm
    top_sash_height=850,   # mm
    bottom_sash_height=850, # mm
    paint_color="White",
    hardware_finish="Satin Chrome",
    bars_layout="3x3"
)

# Add to project
project.add_window(window)

# Save to database
save_project(project)

# Generate exports
create_excel_report(project)
create_pdf_report(project, window)
draw_window(window)
```

### Calculate Multiple Windows

```python
# Create windows with different specifications
windows = [
    calculate_window("W-1", 1200, 1800, 850, 850, bars_layout="3x3"),
    calculate_window("W-2", 900, 1500, 700, 700, bars_layout="2x2"),
    calculate_window("W-3", 600, 1200, 550, 550, frosted=True)
]

for window in windows:
    project.add_window(window)
```

## Configuration Options

### Paint Colors
- White
- Cream
- Custom RAL colors

### Hardware Finishes
- Satin Chrome
- Polished Brass
- Bronze
- Satin Nickel

### Glass Types
- 24mm TGH/ARG/TGH (standard)
- Custom specifications
- Frosted option
- Toughened option

### Glazing Bar Layouts
- None
- 2x2
- 3x3
- 4x4
- Custom

## Database Setup (Optional)

If you want to use Supabase for data storage:

1. Create a Supabase project at https://supabase.com
2. Create the following tables:

```sql
-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    client_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Windows table
CREATE TABLE windows (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name TEXT NOT NULL,
    frame_width NUMERIC,
    frame_height NUMERIC,
    paint_color TEXT,
    hardware_finish TEXT,
    trickle_vent TEXT,
    sash_catches TEXT,
    cill_extension INTEGER
);

-- Materials table
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    window_id UUID REFERENCES windows(id),
    material_type TEXT,
    section TEXT,
    length NUMERIC,
    qty INTEGER,
    wood_type TEXT
);

-- Glass table
CREATE TABLE glass (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    window_id UUID REFERENCES windows(id),
    sash_position TEXT,
    width NUMERIC,
    height NUMERIC,
    type TEXT,
    pcs INTEGER,
    spacer_color TEXT,
    toughened BOOLEAN,
    frosted BOOLEAN
);
```

3. Add your credentials to `.env`

## Output Files

All generated files are saved to the `output/` directory:

- `{ProjectName}.xlsx` - Excel workbook
- `{WindowName}_report.pdf` - PDF report per window
- `{WindowName}_drawing.png` - Technical drawing per window

## Development

### Running Tests
```bash
python main.py
```

### Adding New Features
The modular structure makes it easy to extend:
- Add new calculations in `calculations.py`
- Add new export formats by creating new modules
- Extend data models in `models.py`
- Add new database tables in `database.py`

## Roadmap

- [ ] GUI interface (PyQt/Web)
- [ ] Additional export formats (DXF, SVG)
- [ ] Material cost estimation
- [ ] Weight calculations for sash cords
- [ ] Multi-language support
- [ ] Cloud storage integration

## License

Proprietary - Skylon Elements

## Support

For support, please contact: support@skylon-elements.com

---

**Generated by Claude Code**
**Skylon Elements – Sash Window Designer v1.0**
