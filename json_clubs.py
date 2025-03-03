import csv
import json
import re

def normalize_string(s):
    """
    Remove special characters, convert to lowercase,
    and replace one or more spaces with an underscore.
    """
    cleaned = re.sub(r'[^A-Za-z0-9\s]', '', s)
    cleaned = cleaned.lower().strip()
    normalized = re.sub(r'\s+', '_', cleaned)
    return normalized

CSV_FILE = "json_clubs.csv"
city_groups = {}
default_name_counter = {}

with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Get and normalize the city name (assumed to be in column "City")
        city_raw = row.get("City", "").strip()
        if not city_raw:
            print("Skipping row due to missing City:", row)
            continue
        city_normalized = normalize_string(city_raw)

        # Initialize counter for venues with missing names per city
        if city_normalized not in default_name_counter:
            default_name_counter[city_normalized] = 1

        # Get the venue (club) name; if missing, assign a unique default name
        venue_name = row.get("name", "").strip()
        if not venue_name:
            venue_name = f"venue_{default_name_counter[city_normalized]}"
            default_name_counter[city_normalized] += 1

        # Normalize the club name for URL file naming.
        club_normalized = normalize_string(venue_name)

        # Convert latitude and longitude to float (defaulting to 0.0)
        try:
            lat = float(row.get("lat", "0"))
        except ValueError:
            lat = 0.0
        try:
            lng = float(row.get("lng", "0"))
        except ValueError:
            lng = 0.0

        # Process the activities column (assuming comma-separated)
        activities_str = row.get("activities", "").strip()
        activities = [act.strip() for act in activities_str.split(',')] if activities_str else []

        # Process numeric fields for rating and total ratings
        try:
            rating = float(row.get("rating", "0"))
        except ValueError:
            rating = 0.0
        try:
            user_ratings_total = int(row.get("user_ratings_total", "0"))
        except ValueError:
            user_ratings_total = 0

        # Generate photo URLs (1-5) and logo URL using the normalized city and club name.
        photo_urls = []
        for i in range(1, 6):
            photo_urls.append(
                f"https://raw.githubusercontent.com/uri100/json_pc/refs/heads/main/images/clubs/{city_normalized}/{club_normalized}{i}.jpg"
            )
        logo_url = f"https://raw.githubusercontent.com/uri100/json_pc/refs/heads/main/images/clubs/{city_normalized}/{club_normalized}_logo.png"

        # Create the venue object according to the expected JSON structure.
        venue = {
            "formatted_address": row.get("formatted_address", "").strip(),
            "formatted_phone_number": row.get("formatted_phone_number", "").strip(),
            "geometry": {
                "location": {
                    "lat": lat,
                    "lng": lng
                }
            },
            "name": venue_name,
            "opening_hours": {
                "open_now": False,
                "periods": [],
                "weekday_text": []
            },
            "description": row.get("description", "").strip(),
            "photo_urls": photo_urls,
            "rating": rating,
            "reviews": [],
            "logo": logo_url,
            "user_ratings_total": user_ratings_total,
            "website": row.get("website", "").strip(),
            "activities": activities
        }

        # Group venues by the normalized city name.
        if city_normalized not in city_groups:
            city_groups[city_normalized] = {}
        if venue_name in city_groups[city_normalized]:
            print(f"Warning: Duplicate venue name '{venue_name}' in city '{city_normalized}'. Overwriting previous entry.")
        city_groups[city_normalized][venue_name] = venue

# Write out one JSON file per city using the normalized city name as the filename.
for city_norm, venues in city_groups.items():
    filename = f"{city_norm}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)
    print(f"Created {filename} with {len(venues)} venue(s).")
