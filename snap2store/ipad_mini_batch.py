import os
import sys

from PIL import Image
from psd_tools import PSDImage

# Fixed PSD file path, always based on project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSD_FILE = os.path.join(BASE_DIR, "psd", "iPad-mini-Starlight-Portrait.psd")
# Output directory fixed to output folder in current directory
OUTPUT_DIR = "output"


def process_image(
    screenshot_path, psd_path=PSD_FILE, output_dir=OUTPUT_DIR, transparent=False
):
    """Process single screenshot and generate framed image"""
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

    # Get layer images
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
    if transparent:
        canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    elif bg_img:
        canvas = bg_img.copy()
    else:
        canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))

    # Paste screenshot
    canvas.paste(screenshot, (sc_box[0], sc_box[1]), screenshot)
    # Paste Hardware layer
    canvas.alpha_composite(hw_img, dest=(hw_box[0], hw_box[1]))

    # Output path
    filename = os.path.basename(screenshot_path)
    name, _ = os.path.splitext(filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    extension = "png" if transparent else "jpg"
    output_path = os.path.join(output_dir, f"{name}_framed.{extension}")

    if transparent:
        canvas.save(output_path, "PNG")
    else:
        final_image = canvas.convert("RGB")
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
        print("Usage: python ipad_mini_batch.py <screenshot_file_or_folder_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    main(input_path)
