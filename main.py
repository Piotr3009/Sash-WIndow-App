"""
Main demonstration program for Sash Window Design & Calculation System
Skylon Elements – Sash Window Designer v1.0

This module demonstrates the complete workflow:
1. Create project and windows
2. Calculate all dimensions
3. Save to Supabase database
4. Generate Excel, PDF, and PNG exports
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from models import Project, Window
from calculations import calculate_window
from database import save_project
from export_excel import create_excel_report
from export_pdf import create_pdf_report
from drawings import draw_window


def create_demo_project() -> Project:
    """
    Create a demo project with sample windows

    Returns:
        Project with calculated windows
    """
    print("\n" + "="*60)
    print("  SKYLON ELEMENTS - SASH WINDOW DESIGNER v1.0")
    print("="*60 + "\n")

    # Create project
    project = Project(
        name="Victorian Townhouse Renovation",
        client_name="John Smith Properties Ltd"
    )

    print(f"Creating project: {project.name}")
    print(f"Client: {project.client_name}")
    print(f"Project ID: {project.id}\n")

    # Window 1: Large living room window
    print("Calculating Window W-1 (Living Room)...")
    window1 = calculate_window(
        name="W-1",
        frame_width=1200,
        frame_height=1800,
        top_sash_height=850,
        bottom_sash_height=850,
        paint_color="White",
        hardware_finish="Satin Chrome",
        trickle_vent="Concealed",
        sash_catches="Standard",
        cill_extension=60,
        glass_type="24mm TGH/ARG/TGH",
        bars_layout="3x3",
        spacer_color="Black",
        frosted=False,
        toughened=False
    )
    project.add_window(window1)
    print(f"  ✓ Frame: {window1.frame.width}mm x {window1.frame.height}mm")
    print(f"  ✓ Sash width: {window1.sash_top.width:.1f}mm")
    print(f"  ✓ Glass: {window1.glass_top.width:.1f}mm x {window1.glass_top.height:.1f}mm")
    print(f"  ✓ Bars: {window1.bars_top.layout_type}\n")

    # Window 2: Bedroom window
    print("Calculating Window W-2 (Bedroom)...")
    window2 = calculate_window(
        name="W-2",
        frame_width=900,
        frame_height=1500,
        top_sash_height=700,
        bottom_sash_height=700,
        paint_color="White",
        hardware_finish="Polished Brass",
        trickle_vent="Standard",
        sash_catches="Premium",
        cill_extension=80,
        glass_type="24mm TGH/ARG/TGH",
        bars_layout="2x2",
        spacer_color="White",
        frosted=False,
        toughened=False
    )
    project.add_window(window2)
    print(f"  ✓ Frame: {window2.frame.width}mm x {window2.frame.height}mm")
    print(f"  ✓ Sash width: {window2.sash_top.width:.1f}mm")
    print(f"  ✓ Glass: {window2.glass_top.width:.1f}mm x {window2.glass_top.height:.1f}mm")
    print(f"  ✓ Bars: {window2.bars_top.layout_type}\n")

    # Window 3: Bathroom window (frosted glass)
    print("Calculating Window W-3 (Bathroom)...")
    window3 = calculate_window(
        name="W-3",
        frame_width=600,
        frame_height=1200,
        top_sash_height=550,
        bottom_sash_height=550,
        paint_color="White",
        hardware_finish="Satin Chrome",
        trickle_vent="Concealed",
        sash_catches="Standard",
        cill_extension=40,
        glass_type="24mm TGH/ARG/TGH",
        bars_layout="None",
        spacer_color="Black",
        frosted=True,
        toughened=True
    )
    project.add_window(window3)
    print(f"  ✓ Frame: {window3.frame.width}mm x {window3.frame.height}mm")
    print(f"  ✓ Sash width: {window3.sash_top.width:.1f}mm")
    print(f"  ✓ Glass: {window3.glass_top.width:.1f}mm x {window3.glass_top.height:.1f}mm")
    print(f"  ✓ Frosted & Toughened: Yes\n")

    return project


def export_all_outputs(project: Project):
    """
    Generate all export files (Excel, PDF, PNG)

    Args:
        project: Project to export
    """
    print("="*60)
    print("  GENERATING EXPORTS")
    print("="*60 + "\n")

    # Create Excel report
    print("Generating Excel report...")
    excel_path = create_excel_report(project)
    print(f"  ✓ Excel: {excel_path}\n")

    # Create PDF reports for each window
    print("Generating PDF reports...")
    for window in project.windows:
        pdf_path = create_pdf_report(project, window)
        print(f"  ✓ PDF: {pdf_path}")
    print()

    # Create PNG drawings
    print("Generating technical drawings...")
    for window in project.windows:
        drawing_path = draw_window(window)
        print(f"  ✓ Drawing: {drawing_path}")
    print()


def print_summary(project: Project):
    """
    Print project summary

    Args:
        project: Project to summarize
    """
    print("\n" + "="*60)
    print("  PROJECT SUMMARY")
    print("="*60 + "\n")

    print(f"Project: {project.name}")
    print(f"Client: {project.client_name}")
    print(f"Windows: {len(project.windows)}")
    print(f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"Project ID: {project.id}\n")

    # Window details
    print("Windows:")
    for i, window in enumerate(project.windows, 1):
        print(f"  {i}. {window.name}:")
        print(f"     - Frame: {window.frame.width}mm × {window.frame.height}mm")
        print(f"     - Paint: {window.paint_color}")
        print(f"     - Hardware: {window.hardware_finish}")
        print(f"     - Bars: {window.bars_top.layout_type}")

    # Calculate totals
    total_timber = 0
    total_glass_area = 0

    for window in project.windows:
        from calculations import get_cutting_list
        cutting_list = get_cutting_list(window)
        for item in cutting_list:
            total_timber += item['length'] * item['qty']

        total_glass_area += (window.glass_top.width * window.glass_top.height) / 1000000
        total_glass_area += (window.glass_bottom.width * window.glass_bottom.height) / 1000000

    print(f"\nTotal Timber: {total_timber / 1000:.2f} m")
    print(f"Total Glass Area: {total_glass_area:.2f} m²")
    print(f"Total Panes: {len(project.windows) * 2}")

    print("\n" + "="*60)
    print("  FILES GENERATED")
    print("="*60 + "\n")

    # List generated files
    print(f"Excel Report:")
    print(f"  → output/{project.name.replace(' ', '_')}.xlsx\n")

    print(f"PDF Reports:")
    for window in project.windows:
        print(f"  → output/{window.name}_report.pdf")

    print(f"\nTechnical Drawings:")
    for window in project.windows:
        print(f"  → output/{window.name}_drawing.png")

    print("\n" + "="*60 + "\n")


def main():
    """Main program execution"""

    # Load environment variables
    load_dotenv()

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    try:
        # Step 1: Create demo project with windows
        project = create_demo_project()

        # Step 2: Save to Supabase database
        print("="*60)
        print("  SAVING TO DATABASE")
        print("="*60 + "\n")
        save_project(project)
        print()

        # Step 3: Generate all exports
        export_all_outputs(project)

        # Step 4: Print summary
        print_summary(project)

        print("✓ SUCCESS! All operations completed successfully.")
        print("\nCheck the 'output' directory for all generated files.\n")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
