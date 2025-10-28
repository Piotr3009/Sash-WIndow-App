"""
Database interface using Supabase (PostgreSQL)
Handles all CRUD operations for projects and windows
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from models import Project, Window
from calculations import get_cutting_list


class SupabaseDB:
    """Supabase database interface"""

    def __init__(self):
        """Initialize Supabase client from environment variables"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            print("Warning: SUPABASE_URL and SUPABASE_KEY not set in environment.")
            print("Database operations will be simulated only.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                print("Successfully connected to Supabase")
            except Exception as e:
                print(f"Error connecting to Supabase: {e}")
                self.client = None

    def save_project(self, project: Project) -> Dict[str, Any]:
        """
        Save project to Supabase

        Args:
            project: Project object to save

        Returns:
            Response dictionary from Supabase
        """
        if not self.client:
            print(f"[SIMULATED] Saving project: {project.name}")
            return {"status": "simulated", "data": project.to_dict()}

        try:
            project_data = {
                "id": project.id,
                "name": project.name,
                "client_name": project.client_name,
                "created_at": project.created_at.isoformat()
            }

            response = self.client.table("projects").upsert(project_data).execute()
            print(f"Project saved: {project.name} (ID: {project.id})")
            return {"status": "success", "data": response.data}

        except Exception as e:
            print(f"Error saving project: {e}")
            return {"status": "error", "message": str(e)}

    def save_window(self, window: Window, project_id: str) -> Dict[str, Any]:
        """
        Save window to Supabase

        Args:
            window: Window object to save
            project_id: Parent project ID

        Returns:
            Response dictionary from Supabase
        """
        if not self.client:
            print(f"[SIMULATED] Saving window: {window.name}")
            return {"status": "simulated", "data": window.to_dict()}

        try:
            # Save main window data
            window_data = {
                "id": window.id,
                "project_id": project_id,
                "name": window.name,
                "frame_width": window.frame.width,
                "frame_height": window.frame.height,
                "paint_color": window.paint_color,
                "hardware_finish": window.hardware_finish,
                "trickle_vent": window.trickle_vent,
                "sash_catches": window.sash_catches,
                "cill_extension": window.cill_extension
            }

            response = self.client.table("windows").upsert(window_data).execute()

            # Save materials (cutting list)
            self._save_materials(window)

            # Save glass
            self._save_glass(window)

            print(f"Window saved: {window.name} (ID: {window.id})")
            return {"status": "success", "data": response.data}

        except Exception as e:
            print(f"Error saving window: {e}")
            return {"status": "error", "message": str(e)}

    def _save_materials(self, window: Window):
        """Save materials/cutting list for window"""
        if not self.client:
            return

        try:
            cutting_list = get_cutting_list(window)

            materials = []
            for item in cutting_list:
                materials.append({
                    "window_id": window.id,
                    "material_type": "Timber",
                    "section": item['section'],
                    "length": item['length'],
                    "qty": item['qty'],
                    "wood_type": item['wood_type']
                })

            if materials:
                self.client.table("materials").insert(materials).execute()

        except Exception as e:
            print(f"Error saving materials: {e}")

    def _save_glass(self, window: Window):
        """Save glass specifications for window"""
        if not self.client:
            return

        try:
            glass_data = [
                {
                    "window_id": window.id,
                    "sash_position": "top",
                    "width": window.glass_top.width,
                    "height": window.glass_top.height,
                    "type": window.glass_top.type,
                    "pcs": window.glass_top.pcs,
                    "spacer_color": window.glass_top.spacer_color,
                    "toughened": window.glass_top.toughened,
                    "frosted": window.glass_top.frosted
                },
                {
                    "window_id": window.id,
                    "sash_position": "bottom",
                    "width": window.glass_bottom.width,
                    "height": window.glass_bottom.height,
                    "type": window.glass_bottom.type,
                    "pcs": window.glass_bottom.pcs,
                    "spacer_color": window.glass_bottom.spacer_color,
                    "toughened": window.glass_bottom.toughened,
                    "frosted": window.glass_bottom.frosted
                }
            ]

            self.client.table("glass").insert(glass_data).execute()

        except Exception as e:
            print(f"Error saving glass: {e}")

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve project by ID

        Args:
            project_id: Project ID

        Returns:
            Project data dictionary or None
        """
        if not self.client:
            print(f"[SIMULATED] Getting project: {project_id}")
            return None

        try:
            response = self.client.table("projects").select("*").eq("id", project_id).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            print(f"Error getting project: {e}")
            return None

    def get_window(self, window_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve window by ID

        Args:
            window_id: Window ID

        Returns:
            Window data dictionary or None
        """
        if not self.client:
            print(f"[SIMULATED] Getting window: {window_id}")
            return None

        try:
            response = self.client.table("windows").select("*").eq("id", window_id).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            print(f"Error getting window: {e}")
            return None

    def get_project_windows(self, project_id: str) -> list:
        """
        Get all windows for a project

        Args:
            project_id: Project ID

        Returns:
            List of window data dictionaries
        """
        if not self.client:
            print(f"[SIMULATED] Getting windows for project: {project_id}")
            return []

        try:
            response = self.client.table("windows").select("*").eq("project_id", project_id).execute()
            return response.data if response.data else []

        except Exception as e:
            print(f"Error getting project windows: {e}")
            return []


# Convenience functions
def get_db() -> SupabaseDB:
    """Get database instance"""
    return SupabaseDB()


def save_project(project: Project) -> Dict[str, Any]:
    """Save project to database"""
    db = get_db()
    result = db.save_project(project)

    # Save all windows
    for window in project.windows:
        db.save_window(window, project.id)

    return result


def save_window(window: Window, project_id: str) -> Dict[str, Any]:
    """Save window to database"""
    db = get_db()
    return db.save_window(window, project_id)


def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Get project from database"""
    db = get_db()
    return db.get_project(project_id)


def get_window(window_id: str) -> Optional[Dict[str, Any]]:
    """Get window from database"""
    db = get_db()
    return db.get_window(window_id)
