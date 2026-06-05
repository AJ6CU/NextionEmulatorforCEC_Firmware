from PIL import Image, ImageDraw, ImageEnhance


def create_tech_feedback_buttons(size=100):
    # Hex Colors mapping directly to your requested RGB values
    ELECTRIC_BLUE = (41, 182, 246, 255)  # #29B6F6 (Up Frequency)
    DEEP_INDIGO = (63, 81, 181, 255)  # #3F51B5 (Down Frequency)
    WHITE = (255, 255, 255, 255)

    # 1. Base Geometry Drawing Function
    def draw_base_arrow(color):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        padding = max(2, int(size * 0.03))
        draw.ellipse([padding, padding, size - padding, size - padding], fill=color)

        arrow_vertices = [
            (size * 0.50, size * 0.22), (size * 0.25, size * 0.48),
            (size * 0.40, size * 0.48), (size * 0.40, size * 0.78),
            (size * 0.60, size * 0.78), (size * 0.60, size * 0.48),
            (size * 0.75, size * 0.48)
        ]
        draw.polygon(arrow_vertices, fill=WHITE)
        return img

    # 2. Generate the base "Up" image (#29B6F6)
    up_normal = draw_base_arrow(ELECTRIC_BLUE)
    up_normal.save("../arrow_up_normal.png", "PNG")

    # 3. Generate the base "Down" image (#3F51B5) and rotate it 180 degrees
    down_normal = draw_base_arrow(DEEP_INDIGO).rotate(180, resample=Image.Resampling.BICUBIC)
    down_normal.save("../arrow_down_normal.png", "PNG")

    # 4. Generate the "Pressed" feedback versions by dropping brightness to 70%
    enhancer_up = ImageEnhance.Brightness(up_normal)
    up_pressed = enhancer_up.enhance(0.7)
    up_pressed.save("../arrow_up_pressed.png", "PNG")

    enhancer_down = ImageEnhance.Brightness(down_normal)
    down_pressed = enhancer_down.enhance(0.7)
    down_pressed.save("../arrow_down_pressed.png", "PNG")

    print("Successfully generated new custom-colored tech asset files!")


if __name__ == "__main__":
    # Feel free to adjust the size parameter here if needed
    create_tech_feedback_buttons(size=125)
