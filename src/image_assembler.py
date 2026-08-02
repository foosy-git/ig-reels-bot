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
    
    # Load the bundled font from the assets folder directly
    # This guarantees the font is always available regardless of OS or sudo permissions!
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundled_font_path = os.path.join(project_root, "assets", "Roboto-Bold.ttf")
    
    main_font = None
    handle_font = None
    try:
        main_font = ImageFont.truetype(bundled_font_path, 110)
        handle_font = ImageFont.truetype(bundled_font_path, 45)
        print(f"Successfully loaded bundled font: {bundled_font_path}")
    except IOError:
        print("Warning: Bundled font not found! Using default PIL font (will be tiny).")
        main_font = ImageFont.load_default()
        handle_font = ImageFont.load_default()
        
    for i, quote in enumerate(quotes):
        # Create a sleek dark grey background
        img = Image.new('RGB', (width, height), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        
        # Add a subtle gradient effect or border (optional aesthetic touch)
        draw.rectangle([20, 20, width-20, height-20], outline=(30, 30, 30), width=4)
        
        # Wrap text so it fits beautifully in the center
        # At size 110, we can safely fit about 16-18 characters across 1080 pixels
        wrapped_text = textwrap.fill(quote, width=17)
        
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
