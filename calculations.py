"""
Calculation engine for Sash Window dimensions
Implements all geometry and dimension formulas
"""

from models import Window, Frame, Sash, Glass, Bars


def calculate_frame(frame_width: float, frame_height: float) -> Frame:
    """
    Calculate all frame dimensions

    Args:
        frame_width: Frame width in mm
        frame_height: Frame height in mm

    Returns:
        Frame object with all calculated dimensions
    """
    frame = Frame(
        width=frame_width,
        height=frame_height,
        jambs_length=frame_height - 106,  # Frame height - 106
        head_length=frame_width,
        cill_length=frame_width,
        ext_head_liner=frame_width - 204,  # Frame width - 204
        int_head_liner=frame_width - 170   # Frame width - 170
    )
    return frame


def calculate_sash(frame_width: float, sash_height: float, include_horn: bool = True) -> Sash:
    """
    Calculate sash dimensions

    Args:
        frame_width: Frame width in mm
        sash_height: Sash height in mm
        include_horn: Whether to add horn to top sash (default True)

    Returns:
        Sash object with all calculated dimensions
    """
    sash_width = frame_width - 178  # Frame width - 178

    sash = Sash(
        width=sash_width,
        height=sash_height,
        height_with_horn=sash_height + 70 if include_horn else sash_height,  # Add 70mm horn
        stiles_length=sash_height + 70 if include_horn else sash_height,
        top_rail_length=sash_width,
        bottom_rail_length=sash_width,
        meet_rail_length=sash_width
    )
    return sash


def calculate_glass(sash_width: float, sash_height: float, glass_type: str = "24mm TGH/ARG/TGH",
                    frosted: bool = False, toughened: bool = False,
                    spacer_color: str = "Black") -> Glass:
    """
    Calculate glass dimensions

    Args:
        sash_width: Sash width in mm
        sash_height: Sash height in mm
        glass_type: Glass specification
        frosted: Whether glass is frosted
        toughened: Whether glass is toughened
        spacer_color: Spacer bar color

    Returns:
        Glass object with calculated dimensions
    """
    glass = Glass(
        width=sash_width - 90,   # Sash width - 90
        height=sash_height - 76, # Sash height - 76
        type=glass_type,
        frosted=frosted,
        toughened=toughened,
        spacer_color=spacer_color,
        pcs=1
    )
    return glass


def calculate_bars_spacing(dimension: float, num_bars: int) -> list:
    """
    Calculate equal spacing for glazing bars

    Args:
        dimension: Total dimension (width or height) in mm
        num_bars: Number of bars

    Returns:
        List of spacing values
    """
    if num_bars == 0:
        return []

    spacing = dimension / (num_bars + 1)
    return [spacing] * (num_bars + 1)


def calculate_bars(sash_width: float, sash_height: float, layout_type: str = "None") -> Bars:
    """
    Calculate glazing bars layout

    Args:
        sash_width: Sash width in mm
        sash_height: Sash height in mm
        layout_type: Bar layout ("None", "2x2", "3x3", "Custom")

    Returns:
        Bars object with calculated spacing
    """
    layout_map = {
        "None": (0, 0),
        "2x2": (2, 2),
        "3x3": (3, 3),
        "4x4": (4, 4)
    }

    vertical_bars, horizontal_bars = layout_map.get(layout_type, (0, 0))

    bars = Bars(
        layout_type=layout_type,
        vertical_bars=vertical_bars,
        horizontal_bars=horizontal_bars,
        spacing_vertical=calculate_bars_spacing(sash_width, vertical_bars),
        spacing_horizontal=calculate_bars_spacing(sash_height, horizontal_bars)
    )
    return bars


def calculate_window(
    name: str,
    frame_width: float,
    frame_height: float,
    top_sash_height: float,
    bottom_sash_height: float,
    paint_color: str = "White",
    hardware_finish: str = "Satin Chrome",
    trickle_vent: str = "Concealed",
    sash_catches: str = "Standard",
    cill_extension: int = 60,
    glass_type: str = "24mm TGH/ARG/TGH",
    bars_layout: str = "None",
    spacer_color: str = "Black",
    frosted: bool = False,
    toughened: bool = False
) -> Window:
    """
    Calculate complete window with all components

    Args:
        name: Window identifier (e.g., "W-1")
        frame_width: Frame width in mm
        frame_height: Frame height in mm
        top_sash_height: Top sash height in mm
        bottom_sash_height: Bottom sash height in mm
        paint_color: Paint color specification
        hardware_finish: Hardware finish type
        trickle_vent: Trickle vent type
        sash_catches: Sash catches type
        cill_extension: Cill extension in mm
        glass_type: Glass specification
        bars_layout: Glazing bars layout
        spacer_color: Spacer bar color
        frosted: Frosted glass option
        toughened: Toughened glass option

    Returns:
        Complete Window object with all calculated dimensions
    """
    # Calculate frame
    frame = calculate_frame(frame_width, frame_height)

    # Calculate top sash (with horn)
    sash_top = calculate_sash(frame_width, top_sash_height, include_horn=True)

    # Calculate bottom sash (with horn)
    sash_bottom = calculate_sash(frame_width, bottom_sash_height, include_horn=True)

    # Calculate glass for both sashes
    glass_top = calculate_glass(sash_top.width, sash_top.height, glass_type,
                                frosted, toughened, spacer_color)
    glass_bottom = calculate_glass(sash_bottom.width, sash_bottom.height, glass_type,
                                   frosted, toughened, spacer_color)

    # Calculate bars for both sashes
    bars_top = calculate_bars(sash_top.width, sash_top.height, bars_layout)
    bars_bottom = calculate_bars(sash_bottom.width, sash_bottom.height, bars_layout)

    # Create window object
    window = Window(
        name=name,
        frame=frame,
        sash_top=sash_top,
        sash_bottom=sash_bottom,
        glass_top=glass_top,
        glass_bottom=glass_bottom,
        bars_top=bars_top,
        bars_bottom=bars_bottom,
        paint_color=paint_color,
        hardware_finish=hardware_finish,
        trickle_vent=trickle_vent,
        sash_catches=sash_catches,
        cill_extension=cill_extension
    )

    return window


def get_cutting_list(window: Window) -> list:
    """
    Generate cutting list for a window

    Args:
        window: Window object

    Returns:
        List of dictionaries with section, qty, length, wood_type
    """
    cutting_list = []

    # Frame components
    cutting_list.append({
        'section': 'Jambs',
        'qty': 2,
        'length': round(window.frame.jambs_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Head',
        'qty': 1,
        'length': round(window.frame.head_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Cill',
        'qty': 1,
        'length': round(window.frame.cill_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Ext Head Liner',
        'qty': 1,
        'length': round(window.frame.ext_head_liner, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Int Head Liner',
        'qty': 1,
        'length': round(window.frame.int_head_liner, 1),
        'wood_type': 'Sapele'
    })

    # Top sash components
    cutting_list.append({
        'section': 'Top Sash - Stiles',
        'qty': 2,
        'length': round(window.sash_top.stiles_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Top Sash - Top Rail',
        'qty': 1,
        'length': round(window.sash_top.top_rail_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Top Sash - Meeting Rail',
        'qty': 1,
        'length': round(window.sash_top.meet_rail_length, 1),
        'wood_type': 'Sapele'
    })

    # Bottom sash components
    cutting_list.append({
        'section': 'Bottom Sash - Stiles',
        'qty': 2,
        'length': round(window.sash_bottom.stiles_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Bottom Sash - Bottom Rail',
        'qty': 1,
        'length': round(window.sash_bottom.bottom_rail_length, 1),
        'wood_type': 'Sapele'
    })
    cutting_list.append({
        'section': 'Bottom Sash - Meeting Rail',
        'qty': 1,
        'length': round(window.sash_bottom.meet_rail_length, 1),
        'wood_type': 'Sapele'
    })

    return cutting_list


def get_shopping_list(window: Window) -> list:
    """
    Generate shopping list for a window

    Args:
        window: Window object

    Returns:
        List of dictionaries with item, qty, specification
    """
    shopping_list = [
        {'item': 'Sash Cord', 'qty': 2, 'specification': '6mm Cotton Core'},
        {'item': 'Weights', 'qty': 4, 'specification': '3.5 kg'},
        {'item': 'Pulleys', 'qty': 4, 'specification': 'Brass'},
        {'item': 'Locks', 'qty': 2, 'specification': 'PAS24'},
        {'item': 'Trickle Vent', 'qty': 1, 'specification': window.trickle_vent},
        {'item': 'Sash Catches', 'qty': 2, 'specification': window.sash_catches},
        {'item': 'Hardware Finish', 'qty': 1, 'specification': window.hardware_finish},
        {'item': 'Paint', 'qty': 1, 'specification': f'Teknos AquaTop - {window.paint_color}'},
    ]

    return shopping_list
