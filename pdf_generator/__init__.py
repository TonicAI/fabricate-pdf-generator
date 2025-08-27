"""
PDF Generator for Load Testing

A comprehensive tool for generating PDFs from SQLite database rows with:
- Form-like layout rendering
- File size inflation for load testing
- Image-based "scanned document" simulation
- Flexible title customization
"""

from .generator import PDFGenerator
from .styles import StyleManager
from .content import ContentGenerator
from .images import ImageGenerator
from .inflation import FileSizeInflator
from .database import DatabaseManager
from .fabricate import FabricateManager, create_progress_callback

__version__ = "1.0.0"
__author__ = "Assistant"

__all__ = [
    "PDFGenerator",
    "StyleManager", 
    "ContentGenerator",
    "ImageGenerator",
    "FileSizeInflator",
    "DatabaseManager",
    "FabricateManager",
    "create_progress_callback"
]
