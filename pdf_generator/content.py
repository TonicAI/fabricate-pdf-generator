"""
PDF content generation and form layout.

This module handles the creation of PDF content, including form layouts,
field formatting, and invisible padding for file size inflation.
"""

from typing import Dict, List, Any
from reportlab.platypus import Paragraph, Spacer
from .styles import StyleManager


class ContentGenerator:
    """Handles PDF content creation and form layout"""
    
    def __init__(self, style_manager: StyleManager, title: str):
        self.styles = style_manager.styles
        self.style_manager = style_manager
        self.title = title
    
    def create_form_content(self, data: Dict[str, Any]) -> List:
        """Generate form-like content from row data"""
        content = []
        
        # Add title
        title_paragraph = Paragraph(self.title, self.styles['FormTitle'])
        content.append(title_paragraph)
        content.append(Spacer(1, 12))
        
        # Add data fields in form layout
        for key, value in data.items():
            # Field label
            label = Paragraph(f"{self._format_field_name(key)}:", self.styles['FormLabel'])
            content.append(label)
            
            # Field value
            value_str = str(value) if value is not None else "N/A"
            value_para = Paragraph(value_str, self.styles['FormValue'])
            content.append(value_para)
        
        return content
    
    def add_padding_content(self, content: List, target_bytes: int) -> List:
        """Add minimal invisible padding content for size inflation"""
        if target_bytes <= 50000:  # Skip padding for smaller files
            return content
        
        padded_content = content.copy()
        invisible_style = self.style_manager.get_invisible_style()
        
        # Add small invisible text blocks (efficient approach)
        for i in range(3):
            padding_text = 'padding' * 100  # 700-char block
            padding_para = Paragraph(padding_text, invisible_style)
            padded_content.append(padding_para)
        
        return padded_content
    
    def _format_field_name(self, field_name: str) -> str:
        """Convert field name to human-readable format"""
        return field_name.replace('_', ' ').title()
