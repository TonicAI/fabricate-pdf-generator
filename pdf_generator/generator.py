"""
Main PDF generator orchestrating all components.

This module contains the primary PDFGenerator class that coordinates
all other components to generate PDFs from database data.
"""

import os
import io
from pathlib import Path
from typing import Dict, List, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image
from PIL import Image as PILImage

from .styles import StyleManager
from .content import ContentGenerator
from .images import ImageGenerator
from .inflation import FileSizeInflator
from .database import DatabaseManager


class PDFGenerator:
    """Main PDF generator orchestrating all components"""
    
    def __init__(self, db_path: str, table_name: str, output_dir: str, 
                 use_image: bool = False, title: str = None):
        """
        Initialize PDF generator with all components.
        
        Args:
            db_path: Path to SQLite database
            table_name: Name of table to process
            output_dir: Directory for output files
            use_image: Whether to use image-based rendering
            title: Custom title (defaults to formatted table name)
        """
        self.db_path = db_path
        self.table_name = table_name
        self.output_dir = Path(output_dir)
        self.use_image = use_image
        self.title = title or table_name.replace('_', ' ').title()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.style_manager = StyleManager()
        self.content_generator = ContentGenerator(self.style_manager, self.title)
        self.image_generator = ImageGenerator(self.title)
        self.db_manager = DatabaseManager(db_path, table_name)
    
    def generate_all_pdfs(self):
        """Generate PDFs for all rows in the database table"""
        print(f"Connecting to database: {self.db_path}")
        print(f"Reading from table: {self.table_name}")
        
        # Validate table exists
        if not self.db_manager.validate_table_exists():
            raise ValueError(f"Table '{self.table_name}' not found in database")
        
        # Get data
        data_rows = self.db_manager.get_all_rows()
        print(f"Found {len(data_rows)} rows to process")
        
        if not data_rows:
            print("No data found in the table")
            return
        
        # Process each row
        generated_files = []
        for i, row_data in enumerate(data_rows):
            try:
                output_path = self._generate_single_pdf(row_data, i)
                generated_files.append(output_path)
                print(f"Generated: {output_path}")
            except Exception as e:
                print(f"Error generating PDF for row {i}: {e}")
        
        # Final report
        self._print_summary(generated_files, data_rows)
    
    def _generate_single_pdf(self, data: Dict[str, Any], row_index: int) -> str:
        """Generate a single PDF from row data"""
        # Parse file size target
        target_kb = FileSizeInflator.parse_file_size(data.get('file_size'), row_index)
        
        # Extract filename if present
        custom_filename = data.get('file_name')
        
        # Prepare display data (exclude metadata columns)
        display_data = {k: v for k, v in data.items() if k not in ['file_size', 'file_name']}
        
        # Generate filename
        if custom_filename:
            # Use custom filename, ensuring it's safe and has .pdf extension
            filename = self._sanitize_filename(str(custom_filename).strip())
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
        else:
            # Use default naming scheme
            filename = f"{row_index}.pdf"
        
        output_path = self.output_dir / filename
        
        # Generate PDF
        if self.use_image:
            self._generate_image_based_pdf(display_data, str(output_path), target_kb)
        else:
            self._generate_direct_pdf(display_data, str(output_path), target_kb)
        
        # Verify file size
        if target_kb:
            FileSizeInflator.check_target_accuracy(str(output_path), target_kb, filename)
        
        return str(output_path)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be safe for filesystem use"""
        import re
        
        # Remove any path components (prevent directory traversal)
        filename = os.path.basename(filename)
        
        # Replace invalid characters with underscores
        # Keep alphanumeric, spaces, hyphens, underscores, and dots
        filename = re.sub(r'[^\w\s\-_.]', '_', filename)
        
        # Replace multiple consecutive spaces/underscores with single underscore
        filename = re.sub(r'[\s_]+', '_', filename)
        
        # Remove leading/trailing underscores and dots
        filename = filename.strip('_.')
        
        # Ensure filename isn't empty
        if not filename:
            filename = "document"
        
        # Limit length to prevent filesystem issues
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def _generate_direct_pdf(self, data: Dict[str, Any], output_path: str, target_kb: Optional[int]):
        """Generate PDF directly from data"""
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        content = self.content_generator.create_form_content(data)
        
        if target_kb:
            content = self.content_generator.add_padding_content(content, target_kb * 1024)
        
        doc.build(content)
        
        if target_kb:
            FileSizeInflator.inflate_to_target_size(output_path, target_kb)
    
    def _generate_image_based_pdf(self, data: Dict[str, Any], output_path: str, target_kb: Optional[int]):
        """Generate PDF from image (simulated scanned document)"""
        # Generate appropriate image
        if target_kb and target_kb > 50:
            image = self.image_generator.generate_large_image(data, target_kb)
        else:
            image = self.image_generator.generate_standard_image(data)
        
        # Create PDF with embedded image
        self._embed_image_in_pdf(image, output_path, target_kb)
    
    def _embed_image_in_pdf(self, image: PILImage.Image, output_path: str, target_kb: Optional[int]):
        """Embed PIL image into PDF document"""
        # Save image to buffer
        img_buffer = io.BytesIO()
        quality = 98 if target_kb and target_kb >= 100 else 95
        image.save(img_buffer, format='JPEG', quality=quality)
        img_buffer.seek(0)
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=36, leftMargin=36,
                              topMargin=36, bottomMargin=36)
        
        # Scale image to fit page
        reportlab_img = self._scale_image_for_pdf(image, img_buffer)
        doc.build([reportlab_img])
        
        # Apply size inflation if needed
        if target_kb:
            FileSizeInflator.inflate_to_target_size(output_path, target_kb)
    
    def _scale_image_for_pdf(self, pil_image: PILImage.Image, img_buffer: io.BytesIO) -> Image:
        """Scale image to fit within PDF page margins"""
        max_width = letter[0] - 72   # 540 points
        max_height = letter[1] - 72  # 720 points
        
        img_width, img_height = pil_image.size
        
        # Calculate scaling to fit within bounds
        width_scale = max_width / img_width
        height_scale = max_height / img_height
        scale_factor = min(width_scale, height_scale, 1.0)
        
        final_width = img_width * scale_factor
        final_height = img_height * scale_factor
        
        return Image(img_buffer, width=final_width, height=final_height)
    
    def _print_summary(self, generated_files: List[str], data_rows: List[Dict]):
        """Print generation summary"""
        print(f"\nCompleted! Generated {len(generated_files)} PDFs in {self.output_dir}")
        
        if self.use_image:
            print("PDFs generated using image-based rendering (simulating scanned documents)")
        
        # Report file size inflation if applicable
        if data_rows and 'file_size' in data_rows[0]:
            target_sizes = []
            for row in data_rows:
                parsed_size = FileSizeInflator.parse_file_size(row.get('file_size'), 0)
                if parsed_size:
                    target_sizes.append(parsed_size)
            
            if target_sizes:
                print(f"Applied file size inflation (target range: {min(target_sizes)}-{max(target_sizes)} KB)")
