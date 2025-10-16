import os
import json
import piexif
from PIL import Image, ExifTags
import gpxpy
import math
import datetime
import argparse
from collections import defaultdict
import pandas as pd

try:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="photo_portfolio_indexer")
except ImportError:
    geolocator = None

worldcities_df = pd.read_csv("assets/worldcities.csv")  # columns: city, country, lat, lng

PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
DEFAULT_IMAGE_DIR = "images"
DEFAULT_JSON_PATH = "images.json"
DEFAULT_GPX_DIR = "GPX_Output"
DEFAULT_THUMBS_DIR = "thumbs"

THUMB_SIZES = [
    ("320", 320),      # Gallery thumbnail
    ("1600", 1600)     # Lightbox thumbnail
]

def norm_path(p):
    p = os.path.normpath(p)
    p = p.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    if p.startswith(".images/"):
        p = "images/" + p[9:]
    return p

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# City/country lookup uses SimpleMaps world cities database (https://simplemaps.com/data/world-cities)
def get_city_country(lat, lon):
    # 1. Try offline lookup (SimpleMaps)
    # Find the closest city within 25km
    subset = worldcities_df.copy()
    subset["distance"] = ((subset["lat"] - lat)**2 + (subset["lng"] - lon)**2).pow(0.5)
    closest = subset.loc[subset["distance"].idxmin()]
    # Calculate haversine for accuracy
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)
        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    dist_km = haversine(lat, lon, closest["lat"], closest["lng"])
    if dist_km < 25:
        return f"{closest['city']}, {closest['country']}"
    # 2. Fallback to geopy lookup
    if geolocator:
        try:
            location = geolocator.reverse((lat, lon), language='en', addressdetails=True, timeout=3)
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
            country = address.get('country')
            if city and country:
                return f"{city}, {country}"
            elif country:
                return country
        except Exception as e:
            print(f"Warning: geopy failed for ({lat},{lon}): {e}")
    # 3. Fallback to raw coordinates
    return f"Unknown City/Country ({lat:.5f},{lon:.5f})"

def dms_coordinates(val):
    deg = int(abs(val))
    min_float = (abs(val) - deg) * 60
    min = int(min_float)
    sec = (min_float - min) * 60
    return ((deg, 1), (min, 1), (int(sec * 100), 100))

def gps_ifd(lat, lon):
    lat_dms = dms_coordinates(lat)
    lon_dms = dms_coordinates(lon)
    return {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: lat_dms,
        piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: lon_dms,
    }

def extract_gps_from_exif(exif_dict):
    gps = exif_dict.get("GPS", {})
    def convert_gps(coord, ref):
        if not coord or not ref:
            return None
        d = coord[0][0] / coord[0][1]
        m = coord[1][0] / coord[1][1]
        s = coord[2][0] / coord[2][1] / 100 if coord[2][1] == 100 else coord[2][0] / coord[2][1]
        result = d + m / 60 + s / 3600
        if ref in [b'S', 'S', b'W', 'W']:
            result = -result
        return result
    lat = convert_gps(gps.get(piexif.GPSIFD.GPSLatitude), gps.get(piexif.GPSIFD.GPSLatitudeRef))
    lon = convert_gps(gps.get(piexif.GPSIFD.GPSLongitude), gps.get(piexif.GPSIFD.GPSLongitudeRef))
    return lat, lon

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

def exif_to_iso8601(dtstr):
    try:
        dt = datetime.datetime.strptime(dtstr, "%Y:%m:%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ""

def get_image_datetime(image_path, debug=False):
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if not exif:
            if debug:
                print(f"[DEBUG] No EXIF data found in {image_path}")
            return None
        dt_str = exif.get(36867) or exif.get(306)
        if not dt_str:
            if debug:
                print(f"[DEBUG] No DateTimeOriginal or DateTime in EXIF for {image_path}")
            return None
        try:
            dt_obj = datetime.datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
            return dt_obj
        except Exception as e:
            if debug:
                print(f"[DEBUG] DateTime format error for {image_path}: {e}")
            return None
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error reading EXIF datetime for {image_path}: {e}")
        return None

def image_has_gps(image_path, debug=False):
    try:
        exif_dict = piexif.load(image_path)
        gps = exif_dict.get("GPS", {})
        has_gps = gps.get(piexif.GPSIFD.GPSLatitude) and gps.get(piexif.GPSIFD.GPSLongitude)
        return bool(has_gps)
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error reading GPS from {image_path}: {e}")
        return False

def all_image_files(image_dir, debug=False):
    files_found = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in PHOTO_EXTENSIONS:
                path = os.path.join(root, file).replace("\\", "/")
                files_found.append(path)
                if debug:
                    print(f"[DEBUG] Found image file: {path}")
    return files_found

def get_all_gpx_points(gpx_dir, debug=False):
    points = []
    for root, dirs, files in os.walk(gpx_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext == '.gpx':
                gpx_file = os.path.join(root, file)
                try:
                    with open(gpx_file, 'r', encoding='utf-8') as f:
                        gpx = gpxpy.parse(f)
                        for track in gpx.tracks:
                            for segment in track.segments:
                                for p in segment.points:
                                    if p.time:
                                        pt_time = p.time
                                        if pt_time.tzinfo:
                                            pt_time = pt_time.astimezone(datetime.timezone.utc)
                                        points.append({
                                            'lat': p.latitude,
                                            'lon': p.longitude,
                                            'time': pt_time
                                        })
                except Exception as e:
                    if debug:
                        print(f"[DEBUG] Error parsing GPX file {gpx_file}: {e}")
    points.sort(key=lambda x: x['time'])
    return points

def format_time(dt):
    return dt.strftime('%Y-%m-%d')

def time_difference_in_days_hours(photo_time, gpx_time):
    delta = gpx_time - photo_time
    seconds = abs(int(delta.total_seconds()))
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    sign = "-" if delta.total_seconds() < 0 else "+"
    return f"{sign}{days}d {hours}h"

def find_nearest_gpx_point(img_dt, gpx_points, window_seconds=3600):
    img_dt_utc = img_dt
    if img_dt_utc.tzinfo:
        img_dt_utc = img_dt_utc.astimezone(datetime.timezone.utc)
    else:
        img_dt_utc = img_dt_utc.replace(tzinfo=datetime.timezone.utc)
    best_point = None
    best_diff = window_seconds
    before = None
    after = None
    for p in gpx_points:
        pt_time = p['time']
        pt_time_naive = pt_time.replace(tzinfo=None)
        img_time_naive = img_dt_utc.replace(tzinfo=None)
        if pt_time_naive <= img_time_naive:
            if (before is None) or (pt_time_naive > before['time'].replace(tzinfo=None)):
                before = p
        if pt_time_naive > img_time_naive:
            if (after is None) or (pt_time_naive < after['time'].replace(tzinfo=None)):
                after = p
        diff = abs((pt_time_naive - img_time_naive).total_seconds())
        if diff < best_diff:
            best_diff = diff
            best_point = p
    return best_point, before, after

# CHANGED: Added build_image_entry for consistent image structure
def build_image_entry(path, title="", tags=None, added="", taken="", original_link="", location="", width="", height=""):
    if tags is None:
        tags = []
    return {
        "path": path,
        "title": title,
        "tags": tags,
        "added": added,
        "taken": taken,
        "original_link": original_link,
        "location": location,
        "width": width,
        "height": height
    }

# --------- THUMBNAIL GENERATION FUNCTIONALITY ---------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def thumb_path(img_path, size):
    filename = os.path.splitext(os.path.basename(img_path))[0]
    return os.path.join(DEFAULT_THUMBS_DIR, f"{filename}_{size}.webp")

def generate_thumbnail(src_path, dest_path, max_width):
    try:
        with Image.open(src_path) as img:
            w, h = img.size
            if w > max_width:
                new_h = int(h * max_width / w)
                img = img.resize((max_width, new_h), Image.LANCZOS)
            img.save(dest_path, "WEBP", quality=85)
    except Exception as e:
        print(f"Error generating thumbnail for {src_path}: {e}")

def generate_thumbnails_for_all(images_dir=DEFAULT_IMAGE_DIR, thumbs_dir=DEFAULT_THUMBS_DIR, sizes=THUMB_SIZES, debug=False):
    ensure_dir(thumbs_dir)
    count = 0
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in PHOTO_EXTENSIONS:
                src_path = os.path.join(root, file)
                for size, max_width in sizes:
                    dest_path = thumb_path(src_path, size)
                    if not os.path.exists(dest_path):
                        generate_thumbnail(src_path, dest_path, max_width)
                        count += 1
                        if debug:
                            print(f"Generated thumbnail: {dest_path}")
                    else:
                        if debug:
                            print(f"Thumbnail already exists: {dest_path}")
    print(f"Thumbnail generation complete. {count} new thumbnails created.")

# ------------ END THUMBNAIL GENERATION ----------------

def integrate_index_and_geotag(gpx_dir, img_dir, json_path, test_mode=False, debug=False, window_seconds=3600, force=False, prune=False):
    # Generate thumbnails first
    print("Generating thumbnails before indexing...")
    generate_thumbnails_for_all(images_dir=img_dir, debug=debug)
    # ... remainder unchanged ...
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        images = data.get("images", [])
    else:
        images = []
    images_by_path = {img["path"]: img for img in images}

    all_image_files_list = all_image_files(img_dir, debug=debug)
    gpx_points = get_all_gpx_points(gpx_dir, debug=debug)

    actions = {
        "added": 0,
        "updated_taken": 0,
        "updated_location": 0,
        "updated_size": 0,
        "skipped": 0,
        "geotag_updated": 0,
        "errors": [],
        "pruned": 0
    }
    detailed_actions = []
    results = []
    updated_paths = set()

    for path in all_image_files_list:
        existing = images_by_path.get(path, {})
        width, height, date_taken, gps_info, error = get_image_metadata(path)

        # CHANGED: Create new entry using template if not in JSON, else merge template for missing fields
        if path not in images_by_path:
            if date_taken:
                iso_taken = exif_to_iso8601(date_taken)
            else:
                iso_taken = ""
            if gps_info:
                lat, lon = get_lat_lon(gps_info)
                if lat is not None and lon is not None:
                    city_country = get_city_country(lat, lon)
                else:
                    city_country = ""
            else:
                city_country = ""
            img = build_image_entry(
                path=path,
                title="",
                tags=[],
                added=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                taken=iso_taken,
                original_link="",
                location=city_country,
                width=width,
                height=height
            )
        else:
            img = dict(existing)
            img["path"] = path
            # Ensure all fields are present (merge with template)
            template = build_image_entry(path)
            img = {**template, **img}

        img_dt = None

        # Only update fields if --force is set or field is missing
        # width/height
        if force or not img.get("width") or not img.get("height"):
            img["width"] = width
            img["height"] = height
            if width and height:
                actions["updated_size"] += 1
                detailed_actions.append(f"Set width/height for {path} to {width}x{height}")

        # taken
        if force or not img.get("taken"):
            if date_taken:
                iso_taken = exif_to_iso8601(date_taken)
                img["taken"] = iso_taken
                try:
                    img_dt = datetime.datetime.strptime(iso_taken, "%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    img_dt = None
                actions["updated_taken"] += 1
                detailed_actions.append(f"Set date taken for {path} to {iso_taken}")
            else:
                img_dt = None
        else:
            # If not updating taken, still set img_dt for geotagging
            try:
                img_dt = datetime.datetime.strptime(img["taken"], "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                img_dt = None

        # added
        if not img.get("added"):
            img["added"] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            actions["added"] += 1
            detailed_actions.append(f"Added new image: {path}")

        # location
        if force or not img.get("location"):
            if gps_info:
                lat, lon = get_lat_lon(gps_info)
                if lat is not None and lon is not None:
                    city_country = get_city_country(lat, lon)
                    img["location"] = city_country
                    if city_country:
                        actions["updated_location"] += 1
                        detailed_actions.append(f"Set location for {path} to {city_country}")

        has_gps = image_has_gps(path, debug=debug)
        best, before, after = None, None, None
        if img_dt:
            best, before, after = find_nearest_gpx_point(img_dt, gpx_points, window_seconds=window_seconds)
        img_time_str = format_time(img_dt) if img_dt else "N/A"
        output_lines = []
        city_country = img.get("location", "Unknown Location")

        if error:
            output_lines.append(f"MISSING TIMESTAMP: {path}")
        elif not img_dt:
            output_lines.append(f"MISSING TIMESTAMP: {path}")
        elif has_gps:
            try:
                exif_dict = piexif.load(path)
                lat, lon = extract_gps_from_exif(exif_dict)
                loc_str = get_city_country(lat, lon)
                output_lines.append(f"SKIP (already geotagged): {path}")
                output_lines.append(f"  Photo geotag: {loc_str}")
                # before/after
                if before:
                    before_loc = get_city_country(before['lat'], before['lon'])
                    diff = time_difference_in_days_hours(img_dt, before['time'].replace(second=0, microsecond=0, tzinfo=None))
                    before_day = before['time'].date().isoformat()
                    warn = " (different day)" if before_day != img_dt.date().isoformat() else ""
                    output_lines.append(f"  Closest Before: {format_time(before['time'])} {before_loc} {diff}{warn}")
                else:
                    output_lines.append("  No GPX point before photo.")
                if after:
                    after_loc = get_city_country(after['lat'], after['lon'])
                    diff = time_difference_in_days_hours(img_dt, after['time'].replace(second=0, microsecond=0, tzinfo=None))
                    # Distance from before to after (if both exist)
                    if before:
                        dist = haversine(before['lat'], before['lon'], after['lat'], after['lon'])
                        dist_str = f"{dist:.1f} km"
                    else:
                        dist_str = ""
                    after_day = after['time'].date().isoformat()
                    warn = " (different day)" if after_day != img_dt.date().isoformat() else ""
                    output_lines.append(f"  Closest After: {format_time(after['time'])} {after_loc} {diff}{warn} {dist_str}")
                else:
                    output_lines.append("  No GPX point after photo.")
            except Exception as e:
                output_lines.append(f"  Error reading geotag: {e}")
        elif best:
            action = "WOULD UPDATE" if test_mode else "UPDATED"
            loc_str = get_city_country(best['lat'], best['lon'])
            output_lines.append(f"{action}: {path} -> {loc_str} at {format_time(best['time'])}")
            if not test_mode:
                try:
                    exif_dict = piexif.load(path)
                    gps_dict = gps_ifd(best['lat'], best['lon'])
                    exif_dict['GPS'].update(gps_dict)
                    exif_bytes = piexif.dump(exif_dict)
                    piexif.insert(exif_bytes, path)
                    actions["geotag_updated"] += 1
                except Exception as e:
                    output_lines.append(f"Error updating {path}: {e}")
            if before and before != best:
                before_loc = get_city_country(before['lat'], before['lon'])
                diff = time_difference_in_days_hours(img_dt, before['time'].replace(second=0, microsecond=0, tzinfo=None))
                before_day = before['time'].date().isoformat()
                warn = " (different day)" if before_day != img_dt.date().isoformat() else ""
                output_lines.append(f"  Closest Before: {format_time(before['time'])} {before_loc} {diff}{warn}")
            if after and after != best:
                after_loc = get_city_country(after['lat'], after['lon'])
                diff = time_difference_in_days_hours(img_dt, after['time'].replace(second=0, microsecond=0, tzinfo=None))
                # Distance from before to after
                if before:
                    dist = haversine(before['lat'], before['lon'], after['lat'], after['lon'])
                    dist_str = f"{dist:.1f} km"
                else:
                    dist_str = ""
                after_day = after['time'].date().isoformat()
                warn = " (different day)" if after_day != img_dt.date().isoformat() else ""
                output_lines.append(f"  Closest After: {format_time(after['time'])} {after_loc} {diff}{warn} {dist_str}")
        else:
            output_lines.append(f"NO MATCH: {path}")
            output_lines.append(f"  Photo Time: {img_time_str}")
            if before:
                before_loc = get_city_country(before['lat'], before['lon'])
                diff = time_difference_in_days_hours(img_dt, before['time'].replace(second=0, microsecond=0, tzinfo=None))
                before_day = before['time'].date().isoformat()
                warn = " (different day)" if before_day != img_dt.date().isoformat() else ""
                output_lines.append(f"  Closest Before: {format_time(before['time'])} {before_loc} {diff}{warn}")
            else:
                output_lines.append("  No GPX point before photo.")
            if after:
                after_loc = get_city_country(after['lat'], after['lon'])
                diff = time_difference_in_days_hours(img_dt, after['time'].replace(second=0, microsecond=0, tzinfo=None))
                # Distance from before to after
                if before:
                    dist = haversine(before['lat'], before['lon'], after['lat'], after['lon'])
                    dist_str = f"{dist:.1f} km"
                else:
                    dist_str = ""
                after_day = after['time'].date().isoformat()
                warn = " (different day)" if after_day != img_dt.date().isoformat() else ""
                output_lines.append(f"  Closest After: {format_time(after['time'])} {after_loc} {diff}{warn} {dist_str}")
            else:
                output_lines.append("  No GPX point after photo.")

        results.append((path, img_dt, "\n".join(output_lines)))
        detailed_actions.append(output_lines[0])
        images_by_path[path] = img
        updated_paths.add(path)

    # Prune: remove metadata for images not present
    pruned_images = []
    if prune:
        pruned = [p for p in images_by_path if p not in updated_paths]
        actions["pruned"] = len(pruned)
        for p in pruned:
            pruned_images.append(images_by_path[p])
            detailed_actions.append(f"Pruned metadata for missing image: {p}")
            del images_by_path[p]

    # Prepare updated_images list for JSON output
    updated_images = list(images_by_path.values())
    with_dates = [img for img in updated_images if img.get("taken") and img.get("taken").strip()]
    without_dates = [img for img in updated_images if not (img.get("taken") and img.get("taken").strip())]
    with_dates.sort(key=lambda img: img["taken"], reverse=True)
    without_dates.sort(key=lambda img: img.get("added", ""), reverse=True)
    updated_images = with_dates + without_dates

    with open(json_path, "w", encoding="utf-8") as f:
        f.write('{\n  "images": [\n')
        for i, img in enumerate(updated_images):
            line = json.dumps(img, ensure_ascii=False, separators=(',', ':'))
            if i < len(updated_images) - 1:
                line += ','
            f.write(f'    {line}\n')
        f.write('  ],\n  "pruned": [\n')
        for i, img in enumerate(pruned_images):
            line = json.dumps(img, ensure_ascii=False, separators=(',', ':'))
            if i < len(pruned_images) - 1:
                line += ','
            f.write(f'    {line}\n')
        f.write('  ]\n}\n')

    results.sort(key=lambda x: (x[1] is not None, x[1]), reverse=True)
    print(f"\n--- Geotag & Index Summary ---")
    print(f"Total image files found: {len(all_image_files_list)}")
    print(f"New images added: {actions['added']}")
    print(f"Images with updated date taken: {actions['updated_taken']}")
    print(f"Images with updated location: {actions['updated_location']}")
    print(f"Images with updated width/height: {actions['updated_size']}")
    print(f"Images with updated geotag: {actions['geotag_updated']}")
    print(f"Images skipped due to errors: {actions['skipped']}")
    print(f"Images pruned: {actions['pruned']}")

    if actions["errors"]:
        print(f"\nErrors encountered:")
        for err in actions["errors"]:
            print(f" - {err}")

    print(f"\nDetailed actions:")
    for detail in detailed_actions:
        print(f" - {detail}")

    print(f"\nimages.json updated, sorted by date taken (most recent first).")

    print(f"\n--- Detailed Geotag Output ---")
    for _, _, text in results:
        print(text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Integrate image indexing and geotagging using GPX files")
    parser.add_argument("--gpxdir", type=str, default=DEFAULT_GPX_DIR, help="Directory containing GPX files")
    parser.add_argument("--imgdir", type=str, default=DEFAULT_IMAGE_DIR, help="Directory containing images")
    parser.add_argument("--jsonpath", type=str, default=DEFAULT_JSON_PATH, help="Path for images.json")
    parser.add_argument("--test", action="store_true", help="Test mode (dry run; no changes made)")
    parser.add_argument("--debug", action="store_true", help="Debug mode (prints detailed information)")
    parser.add_argument("--window", type=int, default=3600, help="Window in seconds to match photo to GPX point")
    parser.add_argument("--force", action="store_true", help="Force update width, height, taken, location even if already present")
    parser.add_argument("--prune", action="store_true", help="Remove images from JSON that are no longer in the directory")
    args = parser.parse_args()

    integrate_index_and_geotag(
        gpx_dir=args.gpxdir,
        img_dir=args.imgdir,
        json_path=args.jsonpath,
        test_mode=args.test,
        debug=args.debug,
        window_seconds=args.window,
        force=args.force,
        prune=args.prune
    )