"""
Fabricate integration for dynamic database generation.

This module provides utilities for generating SQLite databases using
the Fabricate service instead of using pre-existing database files.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from tonic_fabricate import generate


class FabricateManager:
    """Manages Fabricate database generation and integration"""
    
    def __init__(self, workspace: str = 'Default'):
        """
        Initialize Fabricate manager.
        
        Args:
            workspace: Fabricate workspace to use (default: 'Default')
        """
        self.workspace = workspace
        self._temp_db_path: Optional[str] = None
    
    def generate_database(self, 
                         database_name: str,
                         output_dir: Optional[str] = None,
                         overwrite: bool = True,
                         entity: Optional[str] = None,
                         on_progress: Optional[Callable] = None) -> str:
        """
        Generate a SQLite database using Fabricate.
        
        Args:
            database_name: Name of the database schema in Fabricate
            output_dir: Directory to save the database (defaults to ./fabricate/<database>_<timestamp>)
            overwrite: Whether to overwrite existing files (default: True)
            entity: Optional specific table/entity to generate
            on_progress: Optional progress callback function
            
        Returns:
            Path to the generated SQLite database file
            
        Raises:
            Exception: If Fabricate generation fails
        """
        if output_dir is None:
            # Use "fabricate" directory in current working directory
            # Create a unique subdirectory for this generation to avoid conflicts
            import time
            timestamp = int(time.time())
            output_path = str(Path.cwd() / "fabricate" / f"{database_name}_{timestamp}")
            # Don't create the directory yet - let Fabricate client handle it
            self._temp_db_path = output_path
        else:
            output_path = str(Path(output_dir).absolute())
            # Don't create the directory yet - let Fabricate client handle it
        
        print(f"Generating database '{database_name}' from Fabricate...")
        print(f"Workspace: {self.workspace}")
        print(f"Output directory: {output_path}")
        
        try:
            # Generate SQLite database using Fabricate (always use sqlite format)
            generate(
                workspace=self.workspace,
                database=database_name,
                format='sqlite',  # Always use SQLite format
                dest=str(output_path),  # Ensure dest is a string, not Path object
                overwrite=overwrite,
                entity=entity,
                on_progress=on_progress or self._default_progress_callback
            )
            
            return output_path
            
        except Exception as e:
            print(f"❌ Failed to generate database: {e}")
            raise
    
    def _default_progress_callback(self, data: Dict[str, Any]):
        """Default progress callback with simple progress display"""
        phase = data.get('phase', '')
        percent = data.get('percentComplete', 0)
        status = data.get('status', '')
        
        phase_text = f"[{phase}] " if phase else ""
        status_text = f", {status}" if status else ""
        print(f"  {phase_text}{percent}% complete{status_text}...")
    
    def cleanup_temp_database(self):
        """Clean up database files if they were created in default location"""
        if self._temp_db_path and os.path.exists(self._temp_db_path):
            import shutil
            try:
                path = Path(self._temp_db_path)
                if path.is_file():
                    path.unlink()
                    print(f"🧹 Cleaned up database file: {self._temp_db_path}")
                elif path.is_dir():
                    shutil.rmtree(self._temp_db_path)
                    print(f"🧹 Cleaned up database directory: {self._temp_db_path}")
            except Exception as e:
                print(f"Warning: Failed to clean up database: {e}")
            finally:
                self._temp_db_path = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temp files"""
        self.cleanup_temp_database()


def create_progress_callback(verbose: bool = True) -> Callable:
    """
    Create a customizable progress callback function.
    
    Args:
        verbose: Whether to show detailed progress information
        
    Returns:
        Progress callback function
    """
    def progress_callback(data: Dict[str, Any]):
        if not verbose:
            return
        
        phase = data.get('phase', '')
        percent = data.get('percentComplete', 0)
        status = data.get('status', '')
        
        # Format progress display
        phase_display = f"📊 {phase}" if phase else "📊 Generating"
        status_display = f" - {status}" if status else ""
        
        # Use different icons based on phase
        icon = "🔄"
        if phase and "complete" in phase.lower():
            icon = "✅"
        elif phase and ("error" in phase.lower() or "fail" in phase.lower()):
            icon = "❌"
        elif phase and "download" in phase.lower():
            icon = "⬇️"
        
        print(f"  {icon} {phase_display}: {percent}%{status_display}")
    
    return progress_callback
