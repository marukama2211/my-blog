import os
import argparse
from PIL import Image

# 対応拡張子
extensions = ['.jpg', '.jpeg', '.png', '.tmp', '.tiff', '.webp']

# コマンドライン引数
parser = argparse.ArgumentParser(description="Convert an image to WebP")
parser.add_argument('filename', type=str, help='Image filename')
parser.add_argument('--dimensions', type=int, default=2048, help='max length')
parser.add_argument('--quality', type=int, default=85, help='quality (0-100, default: 85)')
args = parser.parse_args()

# ファイルパスを探す
file_path = None
for ext in extensions:
    candidate = args.filename + ext
    if os.path.isfile(candidate):
        file_path = candidate
        break

if file_path is None:
    print("File not found.")

# 拡張子の取得
base_name, ext = os.path.splitext(os.path.basename(file_path))
is_webp = ext.lower() == '.webp'
output_path = base_name + '.webp'

try:
    with Image.open(file_path) as img:
        orig_width, orig_height = img.size
        max_orig_dim = max(orig_width, orig_height)
        max_target_dim = min(args.dimensions, max_orig_dim)

        if max_orig_dim == orig_width:
            target_width = max_target_dim
            target_height = int(orig_height * (max_target_dim / orig_width))
        else:
            target_height = max_target_dim
            target_width = int(orig_width * (max_target_dim / orig_height))

        if (target_width, target_height) != (orig_width, orig_height):
            img = img.resize((target_width, target_height), Image.LANCZOS)

        img.save(output_path, format='WEBP', quality=args.quality, lossless=False)

    file_size_kb = os.path.getsize(output_path) / 1024

    print("Conversion complete.")
    print(f"Output file: {output_path}")
    print(f"Pixel: {file_size_kb: .2f} KB")
    print(f"WebP size: {target_width}×{target_height} pz")

except Exception as e:
    print(f"Error occurred: {e}")