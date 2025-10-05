import os
import sys

from PIL import Image
from psd_tools import PSDImage

# Fixed PSD file path, always based on project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSD_FILE = os.path.join(BASE_DIR, "psd", "iPhone17ProMax-DeepBlue-Portrait.psd")
# Output directory fixed to output folder in current directory
OUTPUT_DIR = "output"


def apply_mask_to_image(image, mask):
    """Apply mask to image - simplified version"""
    if mask.mode != "L":
        mask = mask.convert("L")

    # Convert image to RGBA
    image_rgba = image.convert("RGBA")

    # Use mask as alpha channel
    r, g, b, _ = image_rgba.split()
    masked_image = Image.merge("RGBA", (r, g, b, mask))

    return masked_image


def process_image(screenshot_path, psd_path=PSD_FILE, output_dir=OUTPUT_DIR):
    """Process single screenshot and generate JPEG image with device frame"""
    # Open PSD
    psd = PSDImage.open(psd_path)

    # Find target layers
    hardware_layer = None
    screen_layer = None
    background_layer = None

    for layer in psd:
        name_lower = layer.name.lower()
        if layer.name == "Hardware":
            hardware_layer = layer
        elif layer.name == "Screen":
            screen_layer = layer
        elif "background" in name_lower:
            background_layer = layer

    if not hardware_layer or not screen_layer:
        raise RuntimeError("❌ Hardware or Screen layer not found in PSD file")

    # Get layer images and bounding boxes
    hw_img = hardware_layer.composite().convert("RGBA")
    hw_box = hardware_layer.bbox
    sc_box = screen_layer.bbox
    bg_img = background_layer.composite().convert("RGBA") if background_layer else None

    # Open and resize screenshot
    screenshot = Image.open(screenshot_path).convert("RGBA")
    sw, sh = sc_box[2] - sc_box[0], sc_box[3] - sc_box[1]
    screenshot = screenshot.resize((sw, sh), Image.LANCZOS)

    # Create canvas
    canvas_size = psd.size
    if bg_img:
        canvas = bg_img.convert("RGBA")
    else:
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))

    # Correct layer order: Background -> Hardware -> Screenshot (with mask)

    # 1. First paste Hardware layer (below screenshot)
    canvas.alpha_composite(hw_img, dest=(hw_box[0], hw_box[1]))

    # 2. Finally paste screenshot (top layer), apply Screen layer mask
    if screen_layer.mask:
        # Get mask and resize
        mask_img = screen_layer.mask.topil().resize((sw, sh), Image.LANCZOS)

        # Apply mask to screenshot as top layer
        masked_screenshot = apply_mask_to_image(screenshot, mask_img)
        canvas.alpha_composite(masked_screenshot, dest=(sc_box[0], sc_box[1]))
    else:
        print("⚠️ Screen layer has no mask")
        # When no mask, directly paste screenshot as top layer
        canvas.alpha_composite(screenshot, dest=(sc_box[0], sc_box[1]))

    # Remove alpha channel, convert to RGB
    final_image = canvas.convert("RGB")

    # Output path
    filename = os.path.basename(screenshot_path)
    name, _ = os.path.splitext(filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, f"{name}_framed.jpg")

    # Save as JPEG with compression
    final_image.save(output_path, "JPEG", quality=85, optimize=True)
    return output_path


def main(input_path):
    if not os.path.exists(PSD_FILE):
        print(f"❌ PSD file does not exist: {PSD_FILE}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Check if input is file or folder
    if os.path.isfile(input_path):
        print(f"📷 Processing single screenshot: {input_path}")
        out = process_image(input_path)
        print(f"✅ Output: {out}")
    elif os.path.isdir(input_path):
        files = [
            f
            for f in os.listdir(input_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        total = len(files)
        if total == 0:
            print("❌ No screenshot files found in folder")
            return
        print(f"📂 Processing {total} screenshots in folder...")
        for i, f in enumerate(files, start=1):
            path = os.path.join(input_path, f)
            print(f"⏳ Processing {i}/{total}: {f}")
            out = process_image(path)
            print(f"✅ Output: {out}")
        print("🎉 Batch processing completed")
    else:
        print("❌ Input path does not exist")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python iphone_batch.py <screenshot_file_or_folder_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    main(input_path)
