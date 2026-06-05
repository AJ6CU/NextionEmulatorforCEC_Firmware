import os
from PIL import Image, ImageEnhance


def create_disabled_image(input_path, output_path, brightness=1.3, opacity=0.4):
    """
    Opens an image, applies a desaturated, washed-out disabled effect,
    and saves it as a new file. Preserves transparency.
    """
    try:
        # Open image and ensure it has an Alpha (transparency) channel
        img = Image.open(input_path).convert("RGBA")

        # Extract the original alpha mask
        alpha = img.split()[3]

        # Convert color channels to grayscale, keep transparency
        grayscale = img.convert("L").convert("RGBA")
        grayscale.putalpha(alpha)

        # Brighten/wash out the image
        enhancer = ImageEnhance.Brightness(grayscale)
        faded_img = enhancer.enhance(brightness)

        # Apply the opacity reduction to the alpha channel
        final_img = faded_img.copy()
        final_img.putalpha(alpha.point(lambda p: int(p * opacity)))

        # Save the file
        final_img.save(output_path, "PNG")
        print(saved_msg := f"Successfully created: {output_path}")
        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


if __name__ == "__main__":
    # --- CONFIGURATION ---
    # List the exact filenames of the images you want to convert
    images_to_convert = [
        "../arrow_down_normal.png",
        "../arrow_up_normal.png"
    ]

    # Visual tuning
    BRIGHTNESS_LEVEL = 1.3  # > 1.0 washes it out (good for light backgrounds)
    OPACITY_LEVEL = 0.4  # 0.4 means 40% solid, 60% transparent
    # ---------------------

    print("Starting image conversion utility...\n")
    processed_count = 0

    for file_name in images_to_convert:
        if os.path.exists(file_name):
            # Generate a new name (e.g., arrow_left.png -> arrow_left_disabled.png)
            name, ext = os.path.splitext(file_name)
            output_name = f"{name}_disabled.png"

            success = create_disabled_image(
                file_name,
                output_name,
                brightness=BRIGHTNESS_LEVEL,
                opacity=OPACITY_LEVEL
            )
            if success:
                processed_count += 1
        else:
            print(f"Skipped: '{file_name}' not found in this folder.")

    print(f"\nFinished! Processed {processed_count} image(s).")
