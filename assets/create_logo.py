#!/usr/bin/env python3
"""
Simple script to create a Glasfunds logo placeholder.
Replace this with the actual Glasfunds logo PNG when available.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_glasfunds_logo():
    """Create a simple Glasfunds logo placeholder."""
    # Logo dimensions
    width, height = 120, 40
    
    # Glasfunds brand color
    glasfunds_blue = "#005F8C"
    
    # Create image
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background rectangle
    draw.rectangle([0, 0, width-1, height-1], fill=glasfunds_blue, outline=glasfunds_blue)
    
    # Try to use a nice font, fallback to default
    try:
        font = ImageFont.truetype("Arial", 12)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            font = ImageFont.load_default()
    
    # Draw text
    text = "GLASFUNDS"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill="white", font=font)
    
    # Save logo
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    img.save(logo_path)
    print(f"Created logo placeholder at: {logo_path}")
    
    return logo_path

if __name__ == "__main__":
    create_glasfunds_logo() 