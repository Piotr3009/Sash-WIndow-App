"""Supabase persistence layer."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .models import Project, Window

try:  # pragma: no cover - import guard for optional dependency
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - optional dependency not installed
    Client = None  # type: ignore
    create_client = None  # type: ignore


_supabase_client: Optional[Client] = None


def _get_supabase_client() -> Client:
    """Initialise and cache the Supabase client from environment variables."""

    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if create_client is None:
        raise RuntimeError("supabase-py is not installed. Install it to enable database operations.")

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase credentials not configured in environment variables.")

    _supabase_client = create_client(url, key)
    return _supabase_client


def save_project(project: Project) -> Dict[str, Any]:
    """Persist a project record to Supabase."""

    client = _get_supabase_client()
    payload = {
        "id": project.id,
        "name": project.name,
        "client_name": project.client_name,
        "created_at": project.created_at.isoformat(),
    }
    return client.table("projects").upsert(payload).execute()


def save_window(project_id: str, window: Window, materials: List[Dict[str, Any]], glass: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a window and its related material and glass records."""

    client = _get_supabase_client()
    window_payload = {
        "id": window.id,
        "project_id": project_id,
        "name": window.name,
        "frame_width": window.frame.width,
        "frame_height": window.frame.height,
        "paint_color": window.paint_color,
        "hardware_finish": window.hardware_finish,
        "trickle_vent": window.trickle_vent,
        "sash_catches": window.sash_catches,
        "cill_extension": window.cill_extension,
    }

    result = client.table("windows").upsert(window_payload).execute()

    # Replace existing materials/glass for idempotency
    client.table("materials").delete().eq("window_id", window.id).execute()
    client.table("glass").delete().eq("window_id", window.id).execute()

    for item in materials:
        payload = {
            "window_id": window.id,
            "material_type": item.get("material_type"),
            "section": item.get("section"),
            "length": item.get("length"),
            "qty": item.get("qty"),
            "wood_type": item.get("wood_type"),
        }
        client.table("materials").insert(payload).execute()

    glass_payload = {
        "window_id": window.id,
        "width": glass.get("width"),
        "height": glass.get("height"),
        "type": glass.get("type"),
        "pcs": glass.get("pcs"),
        "spacer_color": glass.get("spacer_color"),
        "toughened": glass.get("toughened"),
        "frosted": glass.get("frosted"),
    }
    client.table("glass").upsert(glass_payload).execute()

    return result


def get_project(project_id: str) -> Dict[str, Any]:
    """Fetch a project and its windows from Supabase."""

    client = _get_supabase_client()
    project_response = client.table("projects").select("*").eq("id", project_id).execute()
    windows_response = client.table("windows").select("*").eq("project_id", project_id).execute()

    return {
        "project": project_response.data[0] if project_response.data else None,
        "windows": windows_response.data,
    }


def get_window(window_id: str) -> Dict[str, Any]:
    """Fetch a single window with materials and glass records."""

    client = _get_supabase_client()
    window_response = client.table("windows").select("*").eq("id", window_id).execute()
    materials_response = client.table("materials").select("*").eq("window_id", window_id).execute()
    glass_response = client.table("glass").select("*").eq("window_id", window_id).execute()

    return {
        "window": window_response.data[0] if window_response.data else None,
        "materials": materials_response.data,
        "glass": glass_response.data[0] if glass_response.data else None,
    }
