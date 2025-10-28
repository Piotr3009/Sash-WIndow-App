"""Data models for the Skylon Elements Sash Window Designer backend."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Frame:
    """Represents the outer frame of the window."""

    width: float
    height: float
    jambs_length: float
    head_length: float
    cill_length: float
    ext_head_liner: float
    int_head_liner: float


@dataclass
class Sash:
    """Represents either the top or bottom sash of a sash window."""

    width: float
    height: float
    height_with_horn: float
    stiles_length: float
    top_rail_length: float
    bottom_rail_length: float
    meet_rail_length: float


@dataclass
class Glass:
    """Represents the glazing configuration."""

    width: float
    height: float
    type: str
    frosted: bool
    toughened: bool
    spacer_color: str
    pcs: int


@dataclass
class Bars:
    """Represents bar layout information for decorative glazing bars."""

    layout_type: str
    vertical_bars: int
    horizontal_bars: int
    spacing_vertical: List[float] = field(default_factory=list)
    spacing_horizontal: List[float] = field(default_factory=list)


@dataclass
class Window:
    """Represents a complete sash window with all calculated elements."""

    id: str
    name: str
    frame: Frame
    sash_top: Sash
    sash_bottom: Sash
    glass: Glass
    bars: Bars
    paint_color: str
    hardware_finish: str
    trickle_vent: str
    sash_catches: str
    cill_extension: int


@dataclass
class Project:
    """Represents a collection of windows delivered to a client."""

    id: str
    name: str
    client_name: str
    windows: List[Window] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
