"""
Image generation for scanned document simulation.

This module handles the creation of PIL images with form layouts,
supporting both standard and large image generation for different
file size requirements.
"""

from typing import Dict, Any
from PIL import Image as PILImage, ImageDraw, ImageFont


class ImageGenerator:
    """Handles image generation for scanned document simulation"""
    
    def __init__(self, title: str):
        self.title = title
    
    def generate_standard_image(self, data: Dict[str, Any]) -> PILImage.Image:
        """Generate standard-sized image from data"""
        return self._create_image(data, width=612, height=792, scale_factor=1.0)
    
    def generate_large_image(self, data: Dict[str, Any], target_kb: int) -> PILImage.Image:
        """Generate larger image based on target file size"""
        scale_factor = self._calculate_scale_factor(target_kb)
        base_width, base_height = 612, 792
        
        width = int(base_width * scale_factor)
        height = int(base_height * scale_factor)
        
        return self._create_image(data, width, height, scale_factor, target_kb)
    
    def _calculate_scale_factor(self, target_kb: int) -> float:
        """Calculate appropriate scale factor for target size"""
        if target_kb > 500:
            return min(4.0, target_kb / 250)
        elif target_kb > 100:
            return min(2.5, target_kb / 100)
        else:
            return 1.5
    
    def _create_image(self, data: Dict[str, Any], width: int, height: int, 
                     scale_factor: float, target_kb: int = None) -> PILImage.Image:
        """Create PIL Image with form layout"""
        img = PILImage.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Load fonts with appropriate sizing
        fonts = self._load_fonts(scale_factor)
        
        # Layout content
        y_pos = self._draw_title(draw, width, fonts['title'])
        y_pos = self._draw_form_fields(draw, data, fonts, scale_factor, y_pos, height, target_kb)
        
        return img
    
    def _load_fonts(self, scale_factor: float) -> Dict[str, Any]:
        """Load and size fonts appropriately"""
        try:
            return {
                'title': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(24 * scale_factor)),
                'label': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(16 * scale_factor)),
                'value': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(14 * scale_factor))
            }
        except:
            # Fallback to default fonts
            default_font = ImageFont.load_default()
            return {'title': default_font, 'label': default_font, 'value': default_font}
    
    def _draw_title(self, draw: ImageDraw.Draw, width: int, title_font) -> int:
        """Draw title and return next Y position"""
        y_pos = 50
        title_width = getattr(draw, 'textlength', lambda t, font: len(t) * 12)(self.title, title_font)
        title_x = (width - title_width) // 2
        draw.text((title_x, y_pos), self.title, fill='darkblue', font=title_font)
        return y_pos + 60
    
    def _draw_form_fields(self, draw: ImageDraw.Draw, data: Dict[str, Any], fonts: Dict, 
                         scale_factor: float, start_y: int, height: int, target_kb: int = None) -> int:
        """Draw form fields and return final Y position"""
        x_margin = int(50 * scale_factor)
        y_pos = start_y
        line_spacing = int(40 * scale_factor)
        
        # Determine repetitions for larger files
        repetitions = max(1, min(5, (target_kb or 0) // 200))
        
        for rep in range(repetitions):
            if rep > 0:
                section_text = f"Section {rep + 1}"
                draw.text((x_margin, y_pos), section_text, fill='darkgreen', font=fonts['label'])
                y_pos += line_spacing
            
            for key, value in data.items():
                if y_pos > height - int(100 * scale_factor):
                    return y_pos
                
                # Draw label
                label_text = f"{key.replace('_', ' ').title()}:"
                draw.text((x_margin, y_pos), label_text, fill='black', font=fonts['label'])
                y_pos += int(25 * scale_factor)
                
                # Draw value
                value_str = str(value) if value is not None else "N/A"
                draw.text((x_margin + int(20 * scale_factor), y_pos), value_str, fill='darkgrey', font=fonts['value'])
                y_pos += line_spacing
            
            y_pos += int(30 * scale_factor)  # Section spacing
        
        return y_pos
