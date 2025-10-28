"""
Data models for Sash Window Design & Calculation Program
Defines all entities: Project, Window, Frame, Sash, Glass, Bars
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Frame:
    """Frame dimensions and calculated liner lengths"""
    width: float  # Frame width in mm
    height: float  # Frame height in mm
    jambs_length: float = 0.0  # Calculated: height - 106
    head_length: float = 0.0  # Same as width
    cill_length: float = 0.0  # Same as width
    ext_head_liner: float = 0.0  # Calculated: width - 204
    int_head_liner: float = 0.0  # Calculated: width - 170

    def to_dict(self):
        return asdict(self)


@dataclass
class Sash:
    """Individual sash (top or bottom) dimensions"""
    width: float = 0.0  # Calculated: frame_width - 178
    height: float = 0.0  # User input or calculated
    height_with_horn: float = 0.0  # Calculated: height + 70
    stiles_length: float = 0.0  # Same as height_with_horn
    top_rail_length: float = 0.0  # Same as width
    bottom_rail_length: float = 0.0  # Same as width
    meet_rail_length: float = 0.0  # Same as width (for meeting rail)

    def to_dict(self):
        return asdict(self)


@dataclass
class Glass:
    """Glass specifications for a sash"""
    width: float = 0.0  # Calculated: sash_width - 90
    height: float = 0.0  # Calculated: sash_height - 76
    type: str = "24mm TGH/ARG/TGH"  # Glass type specification
    frosted: bool = False
    toughened: bool = False
    spacer_color: str = "Black"
    pcs: int = 1  # Number of pieces

    def to_dict(self):
        return asdict(self)


@dataclass
class Bars:
    """Glazing bars configuration"""
    layout_type: str = "None"  # "None", "2x2", "3x3", "Custom"
    vertical_bars: int = 0  # Number of vertical bars
    horizontal_bars: int = 0  # Number of horizontal bars
    spacing_vertical: list = field(default_factory=list)  # Spacing between vertical bars
    spacing_horizontal: list = field(default_factory=list)  # Spacing between horizontal bars

    def to_dict(self):
        return asdict(self)


@dataclass
class Window:
    """Complete window specification"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "W-1"
    frame: Frame = field(default_factory=lambda: Frame(0, 0))
    sash_top: Sash = field(default_factory=Sash)
    sash_bottom: Sash = field(default_factory=Sash)
    glass_top: Glass = field(default_factory=Glass)
    glass_bottom: Glass = field(default_factory=Glass)
    bars_top: Bars = field(default_factory=Bars)
    bars_bottom: Bars = field(default_factory=Bars)
    paint_color: str = "White"
    hardware_finish: str = "Satin Chrome"
    trickle_vent: str = "Concealed"
    sash_catches: str = "Standard"
    cill_extension: int = 60  # mm

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'frame': self.frame.to_dict(),
            'sash_top': self.sash_top.to_dict(),
            'sash_bottom': self.sash_bottom.to_dict(),
            'glass_top': self.glass_top.to_dict(),
            'glass_bottom': self.glass_bottom.to_dict(),
            'bars_top': self.bars_top.to_dict(),
            'bars_bottom': self.bars_bottom.to_dict(),
            'paint_color': self.paint_color,
            'hardware_finish': self.hardware_finish,
            'trickle_vent': self.trickle_vent,
            'sash_catches': self.sash_catches,
            'cill_extension': self.cill_extension
        }


@dataclass
class Project:
    """Project containing multiple windows"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Project"
    client_name: str = ""
    windows: list = field(default_factory=list)  # List of Window objects
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'client_name': self.client_name,
            'windows': [w.to_dict() for w in self.windows],
            'created_at': self.created_at.isoformat()
        }

    def add_window(self, window: Window):
        """Add a window to the project"""
        self.windows.append(window)

    def get_window(self, name: str) -> Optional[Window]:
        """Get window by name"""
        for window in self.windows:
            if window.name == name:
                return window
        return None
