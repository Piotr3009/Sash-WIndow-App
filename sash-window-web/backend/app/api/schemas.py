"""Pydantic schemas for the FastAPI layer."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator, validator

from app.core.calculations import assemble_window
from app.core.models import Project, Window


class WindowConfig(BaseModel):
    """Window configuration payload mirroring the PyQt6 GUI options."""

    id: Optional[UUID] = Field(default=None, description="Unique identifier of the window")
    name: str = Field(..., min_length=1, max_length=120)
    frame_width: float = Field(..., gt=0, le=6000)
    frame_height: float = Field(..., gt=0, le=6000)
    top_sash_height: float = Field(..., gt=0, le=4000)
    bottom_sash_height: float = Field(..., gt=0, le=4000)
    paint_color: str = Field(..., min_length=1, max_length=60)
    hardware_finish: str = Field(..., min_length=1, max_length=60)
    trickle_vent: str = Field(..., min_length=1, max_length=60)
    sash_catches: str = Field(..., min_length=1, max_length=60)
    cill_extension: int = Field(ge=0, le=500)
    glass_type: str = Field(..., min_length=1, max_length=120)
    glass_frosted: bool = False
    glass_toughened: bool = False
    spacer_color: str = Field(..., min_length=1, max_length=40)
    glass_pcs: int = Field(..., ge=1, le=10)
    bars_layout: str = Field(..., min_length=1, max_length=40)
    bars_vertical: int = Field(ge=0, le=12)
    bars_horizontal: int = Field(ge=0, le=12)
    wood_type: Optional[str] = Field(default="Sapele", max_length=60)

    @root_validator
    def validate_sash_heights(cls, values: dict) -> dict:
        frame_height = values.get("frame_height")
        top_height = values.get("top_sash_height")
        bottom_height = values.get("bottom_sash_height")
        if frame_height and top_height and bottom_height:
            if top_height + bottom_height > frame_height + 200:  # allow tolerance for horns
                raise ValueError("Sum of sash heights cannot exceed frame height by more than 200 mm.")
        return values

    def to_window(self) -> Window:
        """Convert payload to :class:`Window` dataclass using legacy calculations."""

        window_id = str(self.id or uuid4())
        return assemble_window(
            window_id=window_id,
            name=self.name,
            frame_width=self.frame_width,
            frame_height=self.frame_height,
            top_sash_height=self.top_sash_height,
            bottom_sash_height=self.bottom_sash_height,
            paint_color=self.paint_color,
            hardware_finish=self.hardware_finish,
            trickle_vent=self.trickle_vent,
            sash_catches=self.sash_catches,
            cill_extension=self.cill_extension,
            glass_type=self.glass_type,
            glass_frosted=self.glass_frosted,
            glass_toughened=self.glass_toughened,
            spacer_color=self.spacer_color,
            glass_pcs=self.glass_pcs,
            bars_layout=self.bars_layout,
            bars_vertical=self.bars_vertical,
            bars_horizontal=self.bars_horizontal,
        )


class ProjectConfig(BaseModel):
    """Project level metadata."""

    id: Optional[UUID] = Field(default=None)
    name: str = Field(..., min_length=1, max_length=120)
    client_name: str = Field(..., min_length=1, max_length=120)


class CalculationRequest(BaseModel):
    """Request payload used for both calculation and export endpoints."""

    project: ProjectConfig
    windows: List[WindowConfig]

    @validator("windows")
    def validate_windows(cls, value: List[WindowConfig]) -> List[WindowConfig]:
        if not value:
            raise ValueError("At least one window configuration must be provided.")
        return value

    def to_project(self) -> Project:
        """Build :class:`Project` dataclass with calculated windows."""

        project_id = str(self.project.id or uuid4())
        windows = [window_config.to_window() for window_config in self.windows]
        return Project(
            id=project_id,
            name=self.project.name,
            client_name=self.project.client_name,
            windows=windows,
        )
