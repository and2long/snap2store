<p align="center">
  <img src="docs/logo_snap2store.png" alt="Snap2Store Logo" width="400"/>
</p>

# Snap2Store

[中文文档](docs/README_zh.md)

Snap2Store is designed for Apple developers to solve the problem that screenshots captured from the iOS simulator cannot be directly used in the App Store.  
It automatically adds device frames and adjusts to the required dimensions, making your app screenshots more professional and compliant with App Store standards.

---

## Background

Screenshots taken from the iOS simulator cannot be uploaded directly to the App Store because:
- ❌ Sizes do not match App Store requirements  
- ❌ Missing device frames, resulting in poor presentation  
- ❌ Manual processing is time-consuming and inefficient  

This tool solves these problems with one command:
- ✅ Automatically adds real device frames  
- ✅ Outputs screenshots that meet App Store requirements  
- ✅ Batch processing for improved developer efficiency  

---

## Installation

```bash
# Using pip
pip install -U snap2store

# Or using uv
uv tool install snap2store
```

---

## Usage

### Typical Workflow

1. **Capture screenshots** in the iOS simulator (select the `iPhone 17 Pro Max` or `iPad Pro 13-inch` simulator so the raw captures match Apple’s current App Store device requirements)  
2. **Run the processing tool** for the target device  
3. **Get processed screenshots** with the correct frame and size  
4. **Upload directly** to App Store Connect  

---

### CLI Commands

```bash
# Process a single screenshot (auto-detect device type)
snap2store screenshot.png

# Batch process all screenshots in a folder
snap2store screenshots_folder/

# Specify device type (iPhone)
snap2store -d iphone screenshot.png

# Specify device type (iPad) and custom output directory
snap2store -d ipad -o custom_output/ screenshot.png

# Export transparent background PNG
snap2store --transparent screenshot.png

# Show help
snap2store --help
```

### Command Options

```
usage: snap2store [-h] [-d {iphone,ipad,ipad_mini}] [-o OUTPUT] [--transparent] [-v] input

Snap2Store - Add device bezels to iOS/iPadOS screenshots to meet App Store requirements

positional arguments:
  input                 Screenshot file or folder path

options:
  -h, --help            show this help message and exit
  -d {iphone,ipad,ipad_mini}, --device {iphone,ipad,ipad_mini}
                        Specify device type (auto-detect if not provided)
  -o OUTPUT, --output OUTPUT
                        Output directory (default: ./output/)
  --transparent         Export with transparent background as PNG (default: white background JPG)
  -v, --version         show program's version number and exit

Examples:
  snap2store screenshot.png                  # Auto-detect device type and process single screenshot
  snap2store screenshots/                    # Process all screenshots in the folder
  snap2store -d iphone screenshot.png        # Specify as iPhone screenshot
  snap2store -d ipad -o custom_output/ img/  # Specify as iPad screenshot and custom output directory
  snap2store -d ipad_mini screenshot.png     # Specify as iPad mini screenshot
  snap2store --transparent screenshot.png    # Export transparent background as PNG
```

---

## Local Testing with uv

Run from the project root:

```bash
# Install project dependencies into the uv environment
uv sync

# Check CLI options
uv run snap2store --help

# Test default output: white background JPG
uv run snap2store path/to/screenshot.png

# Test transparent output: transparent background PNG
uv run snap2store --transparent path/to/screenshot.png
```

Expected results:

- Default mode generates `output/<filename>_framed.jpg` with a white background
- `--transparent` generates `output/<filename>_framed.png` with a transparent background

---

## Output

- 📁 Processed files are saved in the `output/` folder  
- 📝 File naming format: `original_filename_framed.jpg` or `original_filename_framed.png`  
- 🎯 **App Store compliant**: correct dimensions and format  
- 🖼️ Default export: white background JPG with quality 85 and optimized compression  
- 🎨 `--transparent` export: transparent background PNG  

---

### Output Dimensions

- 📱 **iPhone**: 1242 × 2688 px  
- 📱 **iPad**: 2064 × 2752 px  

These dimensions fully meet App Store Connect requirements, so the screenshots can be uploaded directly.

---

## Tech Stack

- **Python 3.x**  
- **Pillow (PIL)**: image processing  
- **psd-tools**: PSD file parsing
