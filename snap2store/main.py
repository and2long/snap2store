import argparse
import os
import sys
from typing import List, Optional

from PIL import Image

from snap2store.ipad_batch import process_image as process_ipad
from snap2store.ipad_mini_batch import process_image as process_ipad_mini
from snap2store.iphone_batch import process_image as process_iphone


def is_landscape(img):
    """Check if image is landscape (width greater than height)"""
    width, height = img.size
    return width > height


def detect_device_type(image_path):
    """Determine device type based on image resolution and aspect ratio

    iPad mini: 1488 × 2266 (exact match)
    iPad Pro 13: aspect ratio approximately 4:3 (0.75)
    iPhone: aspect ratio approximately 9:19.5 (0.46)

    Returns:
        (str, bool): (device_type, is_landscape)
        device_type: 'ipad_mini', 'ipad', 'iphone'
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size

            # Check if landscape
            landscape = is_landscape(img)

            # Normalize to portrait orientation for comparison
            portrait_width = min(width, height)
            portrait_height = max(width, height)

            # Check for iPad mini exact resolution (1488 × 2266)
            if portrait_width == 1488 and portrait_height == 2266:
                return 'ipad_mini', landscape

            # Calculate aspect ratio in portrait orientation
            aspect_ratio = portrait_width / portrait_height

            # iPad aspect ratio is close to 3:4 (0.75), iPhone is close to 9:19.5 (0.46)
            # Use 0.6 as threshold for distinction
            if aspect_ratio > 0.6:
                return 'ipad', landscape
            else:
                return 'iphone', landscape
    except Exception as e:
        print(f"❌ Error reading image: {e}")
        return 'unknown', False


def process_auto(image_path, device=None, output_dir="output"):
    """Automatically process screenshot, can specify device type or auto-detect"""
    # Detect device type
    detected_device, landscape = detect_device_type(image_path)

    # If landscape, output error message and exit program
    if landscape:
        print(f"❌ Error: Detected landscape screenshot {image_path}")
        print("❗ Current tool only supports portrait screenshots, cannot process landscape screenshots")
        print("📱 Please try again with portrait screenshots")
        sys.exit(1)

    # If device type is specified by user
    if device:
        if device == "ipad":
            print(f"🔄 Processing iPad screenshot: {image_path}")
            return process_ipad(image_path, output_dir=output_dir)
        elif device == "ipad_mini":
            print(f"🔄 Processing iPad mini screenshot: {image_path}")
            return process_ipad_mini(image_path, output_dir=output_dir)
        else:  # device == "iphone"
            print(f"🔄 Processing iPhone screenshot: {image_path}")
            return process_iphone(image_path, output_dir=output_dir)
    else:
        # Auto-detect device type
        if detected_device == 'ipad_mini':
            print(f"🔍 Detected iPad mini screenshot (1488×2266): {image_path}")
            return process_ipad_mini(image_path, output_dir=output_dir)
        elif detected_device == 'ipad':
            print(f"🔍 Detected iPad screenshot: {image_path}")
            return process_ipad(image_path, output_dir=output_dir)
        elif detected_device == 'iphone':
            print(f"🔍 Detected iPhone screenshot: {image_path}")
            return process_iphone(image_path, output_dir=output_dir)
        else:
            print(f"❌ Unknown device type: {image_path}")
            sys.exit(1)


def process_batch(
    input_dir: str, device: Optional[str] = None, output_dir: str = "output"
) -> List[str]:
    """Batch process all screenshots in folder"""
    processed_files = []

    if not os.path.exists(input_dir):
        print(f"❌ Input directory does not exist: {input_dir}")
        return processed_files

    files = [
        f
        for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    total = len(files)

    if total == 0:
        print("❌ No screenshot files found in folder")
        return processed_files

    print(f"📂 Processing {total} screenshots in folder...")

    for i, f in enumerate(files, start=1):
        path = os.path.join(input_dir, f)
        print(f"⏳ [{i}/{total}] Processing: {f}")
        output_path = process_auto(path, device, output_dir)
        processed_files.append(output_path)

    print(f"✅ Batch processing completed! Processed {len(processed_files)} screenshots")
    return processed_files


def main():
    """CLI main entry function"""
    parser = argparse.ArgumentParser(
        description="Snap2Store - Add device bezels to iOS/iPadOS screenshots to meet App Store requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  snap2store screenshot.png                      # Auto-detect device type and process single screenshot
  snap2store screenshots/                        # Process all screenshots in the folder
  snap2store -d iphone screenshot.png            # Specify as iPhone screenshot
  snap2store -d ipad -o custom_output/ img/      # Specify as iPad screenshot and custom output directory
  snap2store -d ipad_mini screenshot.png         # Specify as iPad mini screenshot
        """,
    )

    parser.add_argument("input", help="Screenshot file or folder path")
    parser.add_argument(
        "-d",
        "--device",
        choices=["iphone", "ipad", "ipad_mini"],
        help="Specify device type (auto-detect if not provided)",
    )
    parser.add_argument(
        "-o", "--output", default="output", help="Output directory (default: ./output/)"
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Ensure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Process input
    input_path = args.input
    if os.path.isdir(input_path):
        process_batch(input_path, args.device, args.output)
    elif os.path.isfile(input_path):
        if input_path.lower().endswith((".png", ".jpg", ".jpeg")):
            output_path = process_auto(input_path, args.device, args.output)
            print(f"✅ Processing completed: {output_path}")
        else:
            print(f"❌ Unsupported file type: {input_path}")
    else:
        print(f"❌ Input path does not exist: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
