from pathlib import Path
from PIL import Image, ImageOps
import shutil

# -----------------------------
# Configuration
# -----------------------------

INPUT_DIR = Path("media/instagram")
OUTPUT_DIR = Path("media/instagram_optimized")

# Resize so neither width nor height exceeds this value.
# Good web default for a scrolling collage background.
MAX_DIMENSION = 1400

# WebP quality: 75-85 is usually a good range for photos.
WEBP_QUALITY = 82

# Valid input types
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

# If True, delete and recreate the output folder each run.
CLEAR_OUTPUT_DIR = True


# -----------------------------
# Helpers
# -----------------------------


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def prepare_output_dir(output_dir: Path) -> None:
    if CLEAR_OUTPUT_DIR and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def collect_images(input_dir: Path) -> list[Path]:
    return sorted([p for p in input_dir.iterdir() if is_image_file(p)], key=lambda p: p.name.lower())


def resize_for_web(img: Image.Image, max_dimension: int) -> Image.Image:
    width, height = img.size
    if max(width, height) <= max_dimension:
        return img

    scale = max_dimension / max(width, height)
    new_size = (round(width * scale), round(height * scale))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def convert_to_webp(src_path: Path, dest_path: Path, max_dimension: int, quality: int) -> tuple[int, int]:
    with Image.open(src_path) as img:
        # Respect EXIF orientation from phones/social images
        img = ImageOps.exif_transpose(img)

        # Convert to RGB for consistent WebP output
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        img = resize_for_web(img, max_dimension)

        # If image has alpha, preserve it. Otherwise save as RGB.
        if img.mode == "RGBA":
            img.save(dest_path, format="WEBP", quality=quality, method=6)
        else:
            img = img.convert("RGB")
            img.save(dest_path, format="WEBP", quality=quality, method=6)

        return img.size


def build_js_constant(files: list[str]) -> str:
    lines = ["const imageFiles = ["]
    for name in files:
        lines.append(f"  '{name}',")
    lines.append("];")
    return "\n".join(lines)


# -----------------------------
# Main
# -----------------------------


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input folder not found: {INPUT_DIR}")

    prepare_output_dir(OUTPUT_DIR)
    source_files = collect_images(INPUT_DIR)

    if not source_files:
        print(f"No image files found in {INPUT_DIR}")
        return

    output_names: list[str] = []

    print(f"Found {len(source_files)} image(s) in {INPUT_DIR}")
    print(f"Writing optimized files to {OUTPUT_DIR}\n")

    for index, src_path in enumerate(source_files, start=1):
        new_name = f"{index:03d}.webp"
        dest_path = OUTPUT_DIR / new_name

        try:
            new_size = convert_to_webp(
                src_path=src_path,
                dest_path=dest_path,
                max_dimension=MAX_DIMENSION,
                quality=WEBP_QUALITY,
            )
            output_names.append(new_name)
            print(f"{src_path.name} -> {new_name}  {new_size[0]}x{new_size[1]}")
        except Exception as e:
            print(f"Skipping {src_path.name}: {e}")

    print("\nDone.\n")
    print(build_js_constant(output_names))


if __name__ == "__main__":
    main()
