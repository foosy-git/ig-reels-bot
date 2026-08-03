import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_carousel_images(quotes, handle="@BeIntentional_Lab"):
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
        main_font = ImageFont.truetype(bundled_font_path, 75)
        handle_font = ImageFont.truetype(bundled_font_path, 35)
        print(f"Successfully loaded bundled font: {bundled_font_path}")
    except IOError:
        print("Warning: Bundled font not found! Using default PIL font (will be tiny).")
        main_font = ImageFont.load_default()
        handle_font = ImageFont.load_default()
        
    for i, quote in enumerate(quotes):
        # Create a clean, minimalist soft white background (executive style)
        img = Image.new('RGB', (width, height), color=(250, 250, 250))
        draw = ImageDraw.Draw(img)
        
        # Wrap text elegantly. With font size 75, width 25 allows for beautiful white space
        wrapped_text = textwrap.fill(quote, width=25)
        
        # Calculate text bounding box to center it perfectly (with generous line spacing)
        left, top, right, bottom = draw.multiline_textbbox((0, 0), wrapped_text, font=main_font, align="center", spacing=35)
        text_width = right - left
        text_height = bottom - top
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        # Draw the main quote in a crisp, dark charcoal (high contrast, authoritative)
        draw.multiline_text((x, y), wrapped_text, fill=(30, 30, 30), font=main_font, align="center", spacing=35)
        
        # Draw a sleek, subtle divider line to anchor the text (a classic Maxwell style element)
        divider_width = 150
        divider_y = height - 180
        draw.line([(width - divider_width) / 2, divider_y, (width + divider_width) / 2, divider_y], fill=(180, 180, 180), width=3)
        
        # Draw the Instagram handle at the bottom center in an understated grey
        handle_left, handle_top, handle_right, handle_bottom = draw.textbbox((0, 0), handle, font=handle_font)
        handle_width = handle_right - handle_left
        handle_x = (width - handle_width) / 2
        handle_y = height - 120
        
        draw.text((handle_x, handle_y), handle, fill=(130, 130, 130), font=handle_font)
        
        # Save the image using a unique ID to prevent race conditions if multiple bots run
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        filename = f"slide_{i+1}_{unique_id}.png"
        filepath = os.path.join(os.getcwd(), filename)
        img.save(filepath)
        output_files.append(filepath)
        print(f"Generated {filename}")
        
    return output_files
