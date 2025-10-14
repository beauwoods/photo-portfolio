import os
import json
from PIL import Image, ExifTags
from datetime import datetime, timezone
import subprocess

try:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="photo_portfolio_indexer")
except ImportError:
    geolocator = None

IMAGE_DIR = "images"
JSON_PATH = "images.json"
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}

def get_image_metadata(img_path):
    width, height = "", ""
    date_taken, gps_info = "", None
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            exif = img._getexif()
            if exif:
                exif_data = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
                date_taken = exif_data.get("DateTimeOriginal", "")
                gps_info = exif_data.get("GPSInfo", None)
    except Exception as e:
        print(f"Error: Could not get metadata for {img_path}: {e}")
        return width, height, date_taken, gps_info, str(e)
    return width, height, date_taken, gps_info, None

def get_lat_lon(gps_info):
    def get_if_exist(data, key):
        return data[key] if key in data else None

    def convert_to_degrees(value):
        d, m, s = value
        return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600

    if not gps_info:
        return None, None
    try:
        lat = convert_to_degrees(get_if_exist(gps_info, 2))
        lon = convert_to_degrees(get_if_exist(gps_info, 4))
        if get_if_exist(gps_info, 1) == 'S':
            lat = -lat
        if get_if_exist(gps_info, 3) == 'W':
            lon = -lon
        return lat, lon
    except Exception:
        return None, None

def get_city_country(lat, lon):
    if geolocator and lat is not None and lon is not None:
        try:
            location = geolocator.reverse((lat, lon), language='en', addressdetails=True)
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
            country = address.get('country')
            if city and country:
                return f"{city}, {country}"
            elif country:
                return country
        except Exception as e:
            print(f"Warning: geopy failed for ({lat},{lon}): {e}")
    return ""

def get_git_added_date(image_path):
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", image_path],
            capture_output=True, text=True, check=True
        )
        date_str = result.stdout.strip().split('\n')[0]
        return date_str if date_str else ""
    except Exception:
        return ""

def exif_to_iso8601(dtstr):
    # EXIF format: 'YYYY:MM:DD HH:MM:SS'
    try:
        dt = datetime.strptime(dtstr, "%Y:%m:%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ""

# Load existing images.json if it exists
if os.path.exists(JSON_PATH):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    images = data.get("images", [])
else:
    images = []

# Build a dict of images by path for fast lookup and update
images_by_path = {img["path"]: img for img in images}

# Scan for all photograph files in the directory
all_image_files = []
for root, dirs, files in os.walk(IMAGE_DIR):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in PHOTO_EXTENSIONS:
            path = os.path.join(root, file).replace("\\", "/")
            all_image_files.append(path)

actions = {
    "added": 0,
    "updated_taken": 0,
    "updated_location": 0,
    "updated_size": 0,
    "skipped": 0,
    "errors": []
}
detailed_actions = []

updated_images = []

for path in all_image_files:
    # Try to preserve all fields from the existing entry
    existing = images_by_path.get(path, {})
    # Extract metadata
    width, height, date_taken, gps_info, error = get_image_metadata(path)

    # Compose the new or updated image entry, preserving all existing fields
    img = dict(existing)  # copy all existing fields (including custom/unknown)
    img["path"] = path

    new_img = path not in images_by_path

    # Only add missing fields or update blank fields
    if not img.get("width") or not img.get("height"):
        img["width"] = width
        img["height"] = height
        if width and height:
            actions["updated_size"] += 1
            detailed_actions.append(f"Set width/height for {path} to {width}x{height}")

    # Handle date taken
    if not img.get("taken"):
        if date_taken:
            iso_taken = exif_to_iso8601(date_taken)
            img["taken"] = iso_taken
            actions["updated_taken"] += 1
            detailed_actions.append(f"Set date taken for {path} to {iso_taken}")
        else:
            git_date = get_git_added_date(path)
            if git_date:
                img["taken"] = git_date
                actions["updated_taken"] += 1
                detailed_actions.append(f"Set date taken for {path} to git added date {git_date}")

    # Handle added date for new images
    if not img.get("added"):
        img["added"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        actions["added"] += 1
        detailed_actions.append(f"Added new image: {path}")

    # Handle location
    if not img.get("location") and gps_info:
        lat, lon = get_lat_lon(gps_info)
        if lat is not None and lon is not None:
            city_country = get_city_country(lat, lon)
            img["location"] = city_country
            if city_country:
                actions["updated_location"] += 1
                detailed_actions.append(f"Set location for {path} to {city_country}")

    if error:
        actions["skipped"] += 1
        actions["errors"].append(f"{path}: {error}")
        detailed_actions.append(f"Skipped {path} (error: {error})")

    updated_images.append(img)

# Optionally, keep images that were in images.json but no longer exist on disk
for path, img in images_by_path.items():
    if path not in all_image_files:
        updated_images.append(img)
        detailed_actions.append(f"Retained metadata for missing image: {path}")

# Sort images by date taken (most recent first), then by added date
with_dates = [img for img in updated_images if img.get("taken") and img.get("taken").strip()]
without_dates = [img for img in updated_images if not (img.get("taken") and img.get("taken").strip())]
# Sort with_dates by taken descending
with_dates.sort(key=lambda img: img["taken"], reverse=True)
# Optionally sort without_dates by "added" descending
without_dates.sort(key=lambda img: img.get("added", ""), reverse=True)
# Concatenate
updated_images = with_dates + without_dates

with open(JSON_PATH, "w", encoding="utf-8") as f:
    f.write('{\n  "images": [\n')
    for i, img in enumerate(updated_images):
        line = json.dumps(img, ensure_ascii=False, separators=(',', ':'))
        if i < len(updated_images) - 1:
            line += ','
        f.write(f'    {line}\n')
    f.write('  ]\n}\n')

# Print summary and details
print(f"--- Image Indexer Summary ---")
print(f"Total image files found: {len(all_image_files)}")
print(f"New images added: {actions['added']}")
print(f"Images with updated date taken: {actions['updated_taken']}")
print(f"Images with updated location: {actions['updated_location']}")
print(f"Images with updated width/height: {actions['updated_size']}")
print(f"Images skipped due to errors: {actions['skipped']}")
if actions["errors"]:
    print(f"\nErrors encountered:")
    for err in actions["errors"]:
        print(f" - {err}")

print(f"\nDetailed actions:")
for detail in detailed_actions:
    print(f" - {detail}")

print(f"\nimages.json updated in required format, sorted by date taken (most recent first).")