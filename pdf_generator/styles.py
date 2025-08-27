"""
Style management for PDF generation.

This module handles all PDF styling and layout configuration,
including custom paragraph styles and formatting options.
"""

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER


class StyleManager:
    """Manages PDF styling and layout configuration"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for forms"""
        self.styles.add(ParagraphStyle(
            name='FormTitle',
            parent=self.styles['Title'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='FormLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='FormValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.darkgrey,
            spaceAfter=12,
            leftIndent=20
        ))
    
    def get_invisible_style(self) -> ParagraphStyle:
        """Get style for invisible padding text"""
        return ParagraphStyle(
            name='Invisible',
            parent=self.styles['Normal'],
            fontSize=1,
            textColor=colors.white,
            spaceAfter=0,
            spaceBefore=0
        )
