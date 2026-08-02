import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_carousel_images(quotes, handle="@yourdailytool_"):
    """
    Generates a series of 1080x1350 (4:5) Instagram Portrait images from a list of quotes.
    Returns a list of file paths.
    """
    width, height = 1080, 1350
    output_files = []
    
    # Try to load a nice font, fallback to default if not found
    font_path = "arial.ttf"
    if os.name == 'nt': # Windows
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        
    try:
        main_font = ImageFont.truetype(font_path, 60)
        handle_font = ImageFont.truetype(font_path, 35)
    except IOError:
        print("Standard font not found, using default PIL font (will not look pretty).")
        main_font = ImageFont.load_default()
        handle_font = ImageFont.load_default()
        
    for i, quote in enumerate(quotes):
        # Create a sleek dark grey background
        img = Image.new('RGB', (width, height), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        
        # Add a subtle gradient effect or border (optional aesthetic touch)
        draw.rectangle([20, 20, width-20, height-20], outline=(30, 30, 30), width=4)
        
        # Wrap text so it fits beautifully in the center
        # Average character width at size 60 is roughly 30px. 
        # So 1080 / 30 = 36 chars per line max. Let's use 30 to be safe and elegant.
        wrapped_text = textwrap.fill(quote, width=30)
        
        # Calculate text bounding box to center it perfectly
        left, top, right, bottom = draw.multiline_textbbox((0, 0), wrapped_text, font=main_font, align="center")
        text_width = right - left
        text_height = bottom - top
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        # Draw the main quote
        draw.multiline_text((x, y), wrapped_text, fill=(245, 245, 245), font=main_font, align="center")
        
        # Draw the Instagram handle at the bottom center
        handle_left, handle_top, handle_right, handle_bottom = draw.textbbox((0, 0), handle, font=handle_font)
        handle_width = handle_right - handle_left
        handle_x = (width - handle_width) / 2
        handle_y = height - 150
        
        draw.text((handle_x, handle_y), handle, fill=(150, 150, 150), font=handle_font)
        
        # Save the image
        filename = f"slide_{i+1}.png"
        filepath = os.path.join(os.getcwd(), filename)
        img.save(filepath)
        output_files.append(filepath)
        print(f"Generated {filename}")
        
    return output_files
