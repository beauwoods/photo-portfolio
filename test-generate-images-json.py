#!/usr/bin/env python3
"""
Test script for generate-images-json.py
Tests the image JSON generation and metadata preservation.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path

# Import the function from generate-images-json.py
import sys
import importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load the module with hyphen in filename
spec = importlib.util.spec_from_file_location(
    "generate_images_json", 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate-images-json.py")
)
generate_images_json_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_images_json_module)

generate_images_json = generate_images_json_module.generate_images_json
load_existing_metadata = generate_images_json_module.load_existing_metadata
get_image_files = generate_images_json_module.get_image_files

def test_basic_generation():
    """Test basic image JSON generation."""
    print("Test 1: Basic generation with sample images...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images directory
        images_dir = os.path.join(tmpdir, 'images')
        os.makedirs(images_dir)
        
        # Create dummy image files
        test_files = ['photo1.jpg', 'photo2.png', 'landscape.jpeg']
        for filename in test_files:
            Path(os.path.join(images_dir, filename)).touch()
        
        output_path = os.path.join(tmpdir, 'images.json')
        
        # Change to tmpdir so relative paths work
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Generate images.json
            generate_images_json('images', 'images.json')
            
            # Verify output
            assert os.path.exists(output_path), "images.json was not created"
            
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # Handle new format
            if isinstance(data, dict) and 'images' in data:
                data = data['images']
            
            assert len(data) == 3, f"Expected 3 images, got {len(data)}"
            assert data[0]['path'] == 'images/landscape.jpeg', f"Expected landscape.jpeg first, got {data[0]['path']}"
            # New images should have empty title (no auto-generation)
            assert data[0]['title'] == '', f"Title should be empty for new images, got {data[0]['title']}"
            assert data[0]['tags'] == [], "Tags should be empty initially"
            # Check that 'added' field exists and is a valid ISO 8601 date
            assert 'added' in data[0], "Missing 'added' field"
            assert data[0]['added'], "'added' field should not be empty"
            
            print("✓ Test 1 passed: Basic generation works correctly")
        finally:
            os.chdir(orig_dir)

def test_metadata_preservation():
    """Test that manual edits to titles and tags are preserved."""
    print("\nTest 2: Metadata preservation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images directory
        images_dir = os.path.join(tmpdir, 'images')
        os.makedirs(images_dir)
        
        # Create dummy image files
        test_files = ['photo1.jpg', 'photo2.png']
        for filename in test_files:
            Path(os.path.join(images_dir, filename)).touch()
        
        output_path = os.path.join(tmpdir, 'images.json')
        
        # Change to tmpdir so relative paths work
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # First generation
            generate_images_json('images', 'images.json')
            
            # Manually edit the JSON (simulating user edits)
            with open(output_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle new format
            if isinstance(json_data, dict) and 'images' in json_data:
                data = json_data['images']
            else:
                data = json_data
            
            data[0]['title'] = 'My Custom Title'
            data[0]['tags'] = ['nature', 'landscape', 'sunset']
            data[1]['title'] = 'Another Custom Title'
            data[1]['tags'] = ['portrait']
            
            # Write back in new format
            with open(output_path, 'w') as f:
                json.dump({'images': data}, f, indent=2)
            
            # Add a new image
            Path(os.path.join(images_dir, 'photo3.jpg')).touch()
            
            # Regenerate images.json
            generate_images_json('images', 'images.json')
            
            # Verify that manual edits are preserved
            with open(output_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle new format
            if isinstance(json_data, dict) and 'images' in json_data:
                new_data = json_data['images']
            else:
                new_data = json_data
            
            assert len(new_data) == 3, f"Expected 3 images, got {len(new_data)}"
            
            # Debug: print the paths
            # print("Paths:", [item['path'] for item in new_data])
            
            # Find the edited images in the new data
            photo1_data = next((item for item in new_data if 'photo1.jpg' in item['path']), None)
            photo2_data = next((item for item in new_data if 'photo2.png' in item['path']), None)
            photo3_data = next((item for item in new_data if 'photo3.jpg' in item['path']), None)
            
            assert photo1_data is not None, "photo1.jpg not found"
            assert photo2_data is not None, "photo2.png not found"
            assert photo3_data is not None, "photo3.jpg not found"
            
            assert photo1_data['title'] == 'My Custom Title', "Title not preserved"
            assert photo1_data['tags'] == ['nature', 'landscape', 'sunset'], "Tags not preserved"
            assert photo2_data['title'] == 'Another Custom Title', "Title not preserved"
            assert photo2_data['tags'] == ['portrait'], "Tags not preserved"
            # New images should have empty title (no auto-generation)
            assert photo3_data['title'] == '', f"New image title should be empty, got {photo3_data['title']}"
            assert photo3_data['tags'] == [], "New image should have empty tags"
            # Check that all images have 'added' field
            assert 'added' in photo1_data, "Missing 'added' field in preserved image"
            assert 'added' in photo3_data, "Missing 'added' field in new image"
            
            print("✓ Test 2 passed: Manual edits are preserved correctly")
        finally:
            os.chdir(orig_dir)

def test_empty_directory():
    """Test behavior with empty images directory."""
    print("\nTest 3: Empty images directory...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        images_dir = os.path.join(tmpdir, 'images')
        os.makedirs(images_dir)
        
        output_path = os.path.join(tmpdir, 'images.json')
        
        # Change to tmpdir so relative paths work
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Generate with no images
            generate_images_json('images', 'images.json')
            
            # Verify empty array is created
            assert os.path.exists(output_path), "images.json was not created"
            
            with open(output_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle new format - should be {"images": []}
            if isinstance(json_data, dict) and 'images' in json_data:
                data = json_data['images']
            else:
                data = json_data
            
            assert data == [], "Expected empty array for no images"
            
            print("✓ Test 3 passed: Empty directory handled correctly")
        finally:
            os.chdir(orig_dir)

def test_image_removal():
    """Test that removed images are not included."""
    print("\nTest 4: Image removal...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        images_dir = os.path.join(tmpdir, 'images')
        os.makedirs(images_dir)
        
        # Create test images
        for filename in ['photo1.jpg', 'photo2.jpg', 'photo3.jpg']:
            Path(os.path.join(images_dir, filename)).touch()
        
        output_path = os.path.join(tmpdir, 'images.json')
        
        # Change to tmpdir so relative paths work
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # First generation
            generate_images_json('images', 'images.json')
            
            with open(output_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle new format
            if isinstance(json_data, dict) and 'images' in json_data:
                data = json_data['images']
            else:
                data = json_data
            
            assert len(data) == 3, "Expected 3 images initially"
            
            # Remove one image
            os.remove(os.path.join(images_dir, 'photo2.jpg'))
            
            # Regenerate
            generate_images_json('images', 'images.json')
            
            with open(output_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle new format
            if isinstance(json_data, dict) and 'images' in json_data:
                data = json_data['images']
            else:
                data = json_data
            
            assert len(data) == 2, f"Expected 2 images after removal, got {len(data)}"
            assert all('photo2.jpg' not in item['path'] for item in data), "Removed image still present"
            
            print("✓ Test 4 passed: Removed images are excluded correctly")
        finally:
            os.chdir(orig_dir)

def test_supported_extensions():
    """Test that only supported image extensions are included."""
    print("\nTest 5: Supported file extensions...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        images_dir = os.path.join(tmpdir, 'images')
        os.makedirs(images_dir)
        
        # Create various files
        test_files = [
            'photo.jpg',
            'photo.jpeg', 
            'photo.png',
            'photo.gif',
            'photo.webp',
            'readme.txt',  # Should be ignored
            'photo.psd',   # Should be ignored
            'data.json'    # Should be ignored
        ]
        
        for filename in test_files:
            Path(os.path.join(images_dir, filename)).touch()
        
        output_path = os.path.join(tmpdir, 'images.json')
        
        # Change to tmpdir so relative paths work
        orig_dir = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            generate_images_json('images', 'images.json')
            
            with open(output_path, 'r') as f:
                json_data = json.load(f)
            
            # Handle new format
            if isinstance(json_data, dict) and 'images' in json_data:
                data = json_data['images']
            else:
                data = json_data
            
            # Should only have 5 valid image files
            assert len(data) == 5, f"Expected 5 images, got {len(data)}"
            
            # Verify non-image files are excluded
            paths = [item['path'] for item in data]
            assert all('.txt' not in p and '.psd' not in p and 'data.json' not in p for p in paths), \
                "Non-image files were included"
            
            print("✓ Test 5 passed: Only supported extensions are included")
        finally:
            os.chdir(orig_dir)

def main():
    """Run all tests."""
    print("=" * 60)
    print("Running tests for generate-images-json.py")
    print("=" * 60)
    
    try:
        test_basic_generation()
        test_metadata_preservation()
        test_empty_directory()
        test_image_removal()
        test_supported_extensions()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
