"""
File size inflation utilities for load testing.

This module provides utilities for parsing file size requirements
from database columns and inflating generated files to meet
target sizes for load testing scenarios.
"""

import os
from typing import Any, Optional


class FileSizeInflator:
    """Handles file size inflation for load testing"""
    
    @staticmethod
    def parse_file_size(file_size_value: Any, row_index: int) -> Optional[int]:
        """
        Parse file size from database value with error handling.
        
        Args:
            file_size_value: Raw value from database (could be string, int, float, etc.)
            row_index: Row number for error reporting
            
        Returns:
            Target size in KB, or None if invalid/missing
        """
        if file_size_value is None:
            return None
        
        try:
            target_kb = int(float(str(file_size_value)))
            return target_kb if target_kb > 0 else None
        except (ValueError, TypeError):
            print(f"Warning: Invalid file_size value '{file_size_value}' for row {row_index}, ignoring")
            return None
    
    @staticmethod
    def inflate_to_target_size(file_path: str, target_kb: int):
        """
        Add binary padding to reach target file size.
        
        Uses efficient large-chunk binary padding that doesn't affect
        PDF functionality while reaching the exact target size.
        
        Args:
            file_path: Path to the PDF file to inflate
            target_kb: Target size in kilobytes
        """
        target_bytes = target_kb * 1024
        current_size = os.path.getsize(file_path)
        
        if current_size >= target_bytes:
            return  # Already at target
        
        padding_needed = target_bytes - current_size
        
        with open(file_path, 'ab') as f:
            f.write(b'\n% Load testing padding data\n')
            
            # Efficient large-chunk padding
            remaining = padding_needed - 30  # Account for header
            if remaining > 0:
                chunk_size = min(65536, remaining)
                base_chunk = b'A' * chunk_size
                
                while remaining > 0:
                    write_size = min(len(base_chunk), remaining)
                    f.write(base_chunk[:write_size])
                    remaining -= write_size
    
    @staticmethod
    def check_target_accuracy(file_path: str, target_kb: int, filename: str, tolerance: float = 0.1):
        """
        Check if file size is within acceptable range of target.
        
        Args:
            file_path: Path to the generated file
            target_kb: Expected size in KB
            filename: Filename for error reporting
            tolerance: Acceptable deviation as fraction (0.1 = 10%)
        """
        final_size = os.path.getsize(file_path)
        final_kb = final_size / 1024
        
        if abs(final_kb - target_kb) > target_kb * tolerance:
            print(f"Warning: {filename} target: {target_kb}KB, actual: {final_kb:.1f}KB")
