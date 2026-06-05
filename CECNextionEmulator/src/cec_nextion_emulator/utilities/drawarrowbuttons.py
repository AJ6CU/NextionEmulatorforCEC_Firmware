from PIL import Image, ImageDraw


def create_parameterized_button(size=100):
    # 1. Create a transparent RGBA canvas based on the parameter size
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 2. Scale the padding proportionally (3% of total size)
    padding = max(2, int(size * 0.03))
    circle_box = [padding, padding, size - padding, size - padding]
    upFill = '#29B6F6' #'#FF9800' #'#4CAF50'
    downFill = '#3F51B5' #'#00BCD4' #'#F44336'
    # draw.ellipse(circle_box, fill=upFill)  # Blue circle
    draw.ellipse(circle_box, fill=downFill)  # Blue circle


    # 3. Parameterized Vector Math for the Up Arrow (calculated as multipliers of 'size')
    # This guarantees the arrow remains perfectly centered at any dimension
    arrow_vertices = [
        (size * 0.50, size * 0.22),  # Pointy tip (exactly centered horizontally)
        (size * 0.25, size * 0.48),  # Left wing tip
        (size * 0.40, size * 0.48),  # Left inner neck
        (size * 0.40, size * 0.78),  # Left bottom base
        (size * 0.60, size * 0.78),  # Right bottom base
        (size * 0.60, size * 0.48),  # Right inner neck
        (size * 0.75, size * 0.48)  # Right wing tip
    ]

    # Draw the solid white arrow
    draw.polygon(arrow_vertices, fill=(255, 255, 255, 255))

    img = img.rotate(180, resample=Image.Resampling.BICUBIC, expand=False)

    # 4. Save file dynamically with its size appended to the name
    # filename = f"../round_up_button.png"
    filename = f"../round_down_button.png"
    img.save(filename, "PNG")
    print(f"Success! Generated a {size}x{size}px asset: '{filename}'")
    return filename


if __name__ == "__main__":
    # Change this parameter value to scale the output button instantly!
    target_size = 125
    create_parameterized_button(size=target_size)
