#!/usr/bin/env python3
"""
Generate images.json from images in the images/ directory.
Preserves manual edits to titles and tags if images.json already exists.
Ensures output preserves order and puts each image object on its own line.
"""

import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}

def get_image_files(images_dir: str) -> List[str]:
    """Get all image files from the images directory."""
    files = []
    for entry in sorted(os.listdir(images_dir)):
        path = os.path.join(images_dir, entry)
        if os.path.isfile(path):
            ext = os.path.splitext(entry)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                files.append(entry)
    return files

def load_existing_metadata(json_path: str) -> Dict[str, Dict[str, Any]]:
    """Load existing metadata from images.json if it exists."""
    metadata = {}

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            # Handle both old format (array) and new format (object with images key)
            if isinstance(existing_data, dict) and 'images' in existing_data:
                existing_data = existing_data['images']
            elif not isinstance(existing_data, list):
                existing_data = []
            # Create a lookup dictionary by path
            for item in existing_data:
                path = item.get('path', '')
                metadata[path] = {
                    'title': item.get('title', ''),
                    'tags': item.get('tags', []),
                    'added': item.get('added', ''),
                    'taken': item.get('taken', ''),
                    'original_link': item.get('original_link', ''),
                    'location': item.get('location', '')
                }
        except Exception as e:
            print(f"Error loading existing images.json: {e}", file=sys.stderr)
    return metadata

def generate_images_json(images_dir: str = 'images', output_path: str = 'images.json'):
    """Generate images.json with metadata, preserve order, one image per line."""
    images_dir_base = os.path.basename(images_dir.rstrip('/'))
    image_files = get_image_files(images_dir)

    if not image_files:
        print(f"No images found in {images_dir}/", file=sys.stderr)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('{"images": []}\n')
        return

    existing_metadata = load_existing_metadata(output_path)

    # Preserve manual order from previous images.json if possible
    prev_order = [p for p in existing_metadata.keys()]
    ordered_files = []
    # Add files in previous order first
    for path in prev_order:
        fname = os.path.basename(path)
        if fname in image_files:
            ordered_files.append(fname)
    # Add new files (not present in previous)
    for fname in image_files:
        full_path = f"{images_dir_base}/{fname}"
        if full_path not in existing_metadata and fname not in ordered_files:
            ordered_files.append(fname)

    images_data = []
    for filename in ordered_files:
        relative_path = f"{images_dir_base}/{filename}"
        if relative_path in existing_metadata:
            title = existing_metadata[relative_path].get('title', '')
            tags = existing_metadata[relative_path].get('tags', [])
            added = existing_metadata[relative_path].get('added', '')
            taken = existing_metadata[relative_path].get('taken', '')
            original_link = existing_metadata[relative_path].get('original_link', '')
            location = existing_metadata[relative_path].get('location', '')
        else:
            title = ''
            tags = []
            added = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            taken = ''
            original_link = ''
            location = ''
        images_data.append({
            'path': relative_path,
            'title': title,
            'tags': tags,
            'added': added,
            'taken': taken,
            'original_link': original_link,
            'location': location
        })

    # Custom dump: one image object per line
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('{\n  "images": [\n')
        for idx, img in enumerate(images_data):
            line = json.dumps(img, ensure_ascii=False)
            # Add comma if not last
            if idx < len(images_data) - 1:
                f.write(f"    {line},\n")
            else:
                f.write(f"    {line}\n")
        f.write('  ]\n}\n')

    print(f"Generated {output_path} with {len(images_data)} images")

def main():
    """Main entry point."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    output_path = os.path.join(script_dir, 'images.json')

    if len(sys.argv) > 1:
        images_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    generate_images_json(images_dir, output_path)

if __name__ == '__main__':
    main()