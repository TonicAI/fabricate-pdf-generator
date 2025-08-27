"""
Database operations for SQLite data access.

This module handles all database connectivity and data retrieval
operations, providing a clean interface for accessing SQLite
database tables.
"""

import sqlite3
from typing import Dict, List, Any


class DatabaseManager:
    """Handles database operations"""
    
    def __init__(self, db_path: str, table_name: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
            table_name: Name of the table to query
        """
        self.db_path = db_path
        self.table_name = table_name
    
    def get_all_rows(self) -> List[Dict[str, Any]]:
        """
        Fetch all rows from the specified table.
        
        Returns:
            List of dictionaries, where each dict represents a row
            with column names as keys
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {self.table_name}")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to query table '{self.table_name}': {e}")
    
    def validate_table_exists(self) -> bool:
        """
        Check if the specified table exists in the database.
        
        Returns:
            True if table exists, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (self.table_name,))
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False
    
    def get_column_names(self) -> List[str]:
        """
        Get list of column names from the table.
        
        Returns:
            List of column names
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({self.table_name})")
                return [row[1] for row in cursor.fetchall()]  # Column name is at index 1
        except sqlite3.Error:
            return []
