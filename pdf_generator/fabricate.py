"""
Fabricate integration for dynamic database generation.

This module provides utilities for generating SQLite databases using
the Fabricate service instead of using pre-existing database files.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Callable

try:
    from fabricate_client import generate
    FABRICATE_AVAILABLE = True
except ImportError:
    FABRICATE_AVAILABLE = False


class FabricateManager:
    """Manages Fabricate database generation and integration"""
    
    def __init__(self, workspace: str = 'Default'):
        """
        Initialize Fabricate manager.
        
        Args:
            workspace: Fabricate workspace to use (default: 'Default')
        """
        if not FABRICATE_AVAILABLE:
            raise ImportError(
                "fabricate-client is not installed. "
                "Install it with: pip install fabricate-client"
            )
        
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
            output_dir: Directory to save the database (defaults to temp)
            overwrite: Whether to overwrite existing files
            entity: Optional specific table/entity to generate
            on_progress: Optional progress callback function
            
        Returns:
            Path to the generated SQLite database file
            
        Raises:
            Exception: If Fabricate generation fails
        """
        if output_dir is None:
            # Use temporary directory
            temp_dir = tempfile.mkdtemp(prefix="fabricate_db_")
            output_path = temp_dir
            self._temp_db_path = temp_dir
        else:
            output_path = str(Path(output_dir).absolute())
            # Ensure the output directory exists
            Path(output_path).mkdir(parents=True, exist_ok=True)
        
        print(f"Generating database '{database_name}' from Fabricate...")
        print(f"Workspace: {self.workspace}")
        print(f"Output directory: {output_path}")
        
        try:
            # Generate SQLite database using Fabricate (always use sqlite format)
            print(f"📡 Calling Fabricate with parameters:")
            print(f"   - workspace: {self.workspace}")
            print(f"   - database: {database_name}")
            print(f"   - format: sqlite")
            print(f"   - dest: {output_path}")
            print(f"   - entity: {entity}")
            
            generate(
                workspace=self.workspace,
                database=database_name,
                format='sqlite',  # Always use SQLite format
                dest=str(output_path),  # Ensure dest is a string, not Path object
                overwrite=overwrite,
                entity=entity,
                unzip=True,  # Explicitly set unzip to True for directory dest
                on_progress=on_progress or self._default_progress_callback
            )
            
            # Find the generated SQLite file
            db_file_path = self._find_sqlite_file(output_path, database_name)
            
            print(f"✅ Database generated successfully: {db_file_path}")
            return db_file_path
            
        except AttributeError as e:
            if "'NoneType' object has no attribute 'lower'" in str(e):
                print(f"❌ Fabricate API Error: Received unexpected response format.")
                print(f"   This usually indicates:")
                print(f"   - Authentication failure (check API key)")
                print(f"   - Workspace '{self.workspace}' doesn't exist")
                print(f"   - Database '{database_name}' doesn't exist in workspace")
                print(f"   - API connectivity issues")
                print(f"   Original error: {e}")
            else:
                print(f"❌ Attribute error: {e}")
            raise
        except Exception as e:
            print(f"❌ Failed to generate database: {e}")
            print(f"   Error type: {type(e).__name__}")
            raise
    
    def _find_sqlite_file(self, output_dir: str, database_name: str) -> str:
        """Find the generated SQLite file in the output directory"""
        output_path = Path(output_dir)
        
        # Look for files with common SQLite extensions
        sqlite_extensions = ['.sqlite', '.sqlite3', '.db']
        
        for ext in sqlite_extensions:
            potential_file = output_path / f"{database_name}{ext}"
            if potential_file.exists():
                return str(potential_file)
        
        # If not found with exact name, look for any SQLite file
        for ext in sqlite_extensions:
            for file_path in output_path.glob(f"*{ext}"):
                return str(file_path)
        
        raise FileNotFoundError(
            f"No SQLite file found in {output_dir} after Fabricate generation"
        )
    
    def _default_progress_callback(self, data: Dict[str, Any]):
        """Default progress callback with simple progress display"""
        phase = data.get('phase', '')
        percent = data.get('percentComplete', 0)
        status = data.get('status', '')
        
        phase_text = f"[{phase}] " if phase else ""
        status_text = f", {status}" if status else ""
        print(f"  {phase_text}{percent}% complete{status_text}...")
    
    def cleanup_temp_database(self):
        """Clean up temporary database files if they were created"""
        if self._temp_db_path and os.path.exists(self._temp_db_path):
            import shutil
            try:
                shutil.rmtree(self._temp_db_path)
                print(f"🧹 Cleaned up temporary database: {self._temp_db_path}")
            except Exception as e:
                print(f"Warning: Failed to clean up temporary database: {e}")
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
        if "complete" in phase.lower():
            icon = "✅"
        elif "error" in phase.lower() or "fail" in phase.lower():
            icon = "❌"
        elif "download" in phase.lower():
            icon = "⬇️"
        
        print(f"  {icon} {phase_display}: {percent}%{status_display}")
    
    return progress_callback
