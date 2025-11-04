
from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory if it doesn't exist
os.makedirs('static/icons', exist_ok=True)

def create_gradient_icon(size, filename):
    """Create a gradient icon with BF logo"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # Create gradient from purple to dark blue
    for y in range(size):
        # Purple (#9333ea) to dark blue (#1a1a2e)
        r = int(147 - (147 - 26) * y / size)
        g = int(51 - (51 - 26) * y / size)
        b = int(234 - (234 - 46) * y / size)
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
    
    # Draw circle background for better maskable support
    circle_radius = int(size * 0.4)
    circle_center = (size // 2, size // 2)
    draw.ellipse(
        [(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
         (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
        fill=(26, 26, 46, 200)
    )
    
    # Draw "BF" text
    try:
        # Try to use a system font, fallback to default if not available
        font_size = int(size * 0.35)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    text = "BF"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - int(size * 0.05)
    
    # Draw text with shadow for depth
    shadow_offset = max(2, size // 100)
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    
    # Draw small robot icon indicator below text
    bot_y = text_y + text_height + int(size * 0.05)
    bot_size = int(size * 0.08)
    draw.ellipse(
        [(circle_center[0] - bot_size, bot_y),
         (circle_center[0] + bot_size, bot_y + bot_size * 2)],
        fill=(147, 51, 234)
    )
    
    # Save the image
    img.save(f'static/icons/{filename}', 'PNG', optimize=True)
    print(f"Created {filename} ({size}x{size})")

def create_maskable_icon(size, filename):
    """Create a maskable icon with safe zone padding"""
    # Maskable icons need 40% safe zone (20% padding on each side)
    padding = int(size * 0.1)  # 10% padding on each side for extra safety
    inner_size = size - (padding * 2)
    
    # Create base image
    img = Image.new('RGB', (size, size), color=(26, 26, 46))
    
    # Create inner icon
    inner_img = Image.new('RGBA', (inner_size, inner_size))
    draw = ImageDraw.Draw(inner_img)
    
    # Gradient background
    for y in range(inner_size):
        r = int(147 - (147 - 26) * y / inner_size)
        g = int(51 - (51 - 26) * y / inner_size)
        b = int(234 - (234 - 46) * y / inner_size)
        draw.rectangle([(0, y), (inner_size, y+1)], fill=(r, g, b))
    
    # Draw circle
    circle_radius = int(inner_size * 0.45)
    circle_center = (inner_size // 2, inner_size // 2)
    draw.ellipse(
        [(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
         (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
        fill=(26, 26, 46)
    )
    
    # Draw text
    try:
        font_size = int(inner_size * 0.4)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    text = "BF"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (inner_size - text_width) // 2
    text_y = (inner_size - text_height) // 2 - int(inner_size * 0.05)
    
    draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 128), font=font)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    
    # Paste inner icon onto base with padding
    img.paste(inner_img, (padding, padding))
    
    # Save
    img.save(f'static/icons/{filename}', 'PNG', optimize=True)
    print(f"Created maskable {filename} ({size}x{size})")

# Generate standard icons
print("Generating PWA icons...")
create_gradient_icon(192, 'icon-192x192.png')
create_gradient_icon(512, 'icon-512x512.png')

# Generate maskable icons
print("\nGenerating maskable icons...")
create_maskable_icon(192, 'icon-192x192-maskable.png')
create_maskable_icon(512, 'icon-512x512-maskable.png')

# Generate additional common sizes
print("\nGenerating additional sizes...")
for size in [72, 96, 128, 144, 152, 180, 384]:
    create_gradient_icon(size, f'icon-{size}x{size}.png')

print("\n✅ All icons generated successfully!")
print("\nGenerated icons:")
print("- Standard icons: 72x72, 96x96, 128x128, 144x144, 152x152, 180x180, 192x192, 384x384, 512x512")
print("- Maskable icons: 192x192, 512x512")
