#!/usr/bin/env python3
"""
Generate images.json from images in the images/ directory.
Preserves manual edits to titles and tags if images.json already exists.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}

def get_image_files(images_dir: str) -> List[str]:
    """Get all image files from the images directory."""
    image_files = []
    
    if not os.path.exists(images_dir):
        return image_files
    
    for filename in sorted(os.listdir(images_dir)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            image_files.append(filename)
    
    return image_files

def load_existing_metadata(json_path: str) -> Dict[str, Dict[str, Any]]:
    """Load existing metadata from images.json if it exists."""
    metadata = {}
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                
            # Create a lookup dictionary by path
            for item in existing_data:
                path = item.get('path', '')
                metadata[path] = {
                    'title': item.get('title', ''),
                    'tags': item.get('tags', [])
                }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read existing images.json: {e}", file=sys.stderr)
    
    return metadata

def generate_images_json(images_dir: str = 'images', output_path: str = 'images.json'):
    """Generate images.json with metadata."""
    
    # Normalize the images_dir to be relative if possible
    images_dir_base = os.path.basename(images_dir.rstrip('/'))
    
    # Get all image files
    image_files = get_image_files(images_dir)
    
    if not image_files:
        print(f"No images found in {images_dir}/", file=sys.stderr)
        # Create empty array if no images
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        return
    
    # Load existing metadata
    existing_metadata = load_existing_metadata(output_path)
    
    # Generate the images array
    images_data = []
    for filename in image_files:
        relative_path = f"{images_dir_base}/{filename}"
        
        # Check if we have existing metadata for this image
        if relative_path in existing_metadata:
            # Preserve manual edits
            title = existing_metadata[relative_path].get('title', '')
            tags = existing_metadata[relative_path].get('tags', [])
        else:
            # Generate default title from filename
            title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
            tags = []
        
        images_data.append({
            'path': relative_path,
            'title': title,
            'tags': tags
        })
    
    # Write the updated images.json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(images_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {output_path} with {len(images_data)} images")
    print(f"Preserved metadata for {len([p for p in images_data if p['path'] in existing_metadata])} existing images")

def main():
    """Main entry point."""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    output_path = os.path.join(script_dir, 'images.json')
    
    # Allow overriding via command line arguments
    if len(sys.argv) > 1:
        images_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    
    generate_images_json(images_dir, output_path)

if __name__ == '__main__':
    main()
