import os
import math
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
# Load environment variables
load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
# Geoapify healthcare categories
FACILITY_TYPES = {
    "hospital": "healthcare.hospital",
    "doctor": "healthcare.clinic_or_praxis",
    "clinic": "healthcare.clinic_or_praxis",
    "pharmacy": "healthcare.pharmacy",
}
def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate straight-line distance
    between two geographic coordinates.
    """
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )
    return earth_radius * c

@tool
def find_nearby_healthcare(
    latitude: float,
    longitude: float,
    facility_type: str = "hospital",
    radius: int = 5000
) -> list[dict]:
    """
    Find nearby hospitals, doctors, clinics,
    and pharmacies using Geoapify Places API.

    latitude:
        User's latitude.

    longitude:
        User's longitude.

    facility_type:
        hospital, doctor, clinic, pharmacy.

    radius:
        Search radius in metres.
        Maximum 50000 metres.

    Coordinates must be supplied by the user
    or application. Never guess coordinates.
    """
    # Check API key

    if not GEOAPIFY_API_KEY:

        return [{
            "error": (
                "GEOAPIFY_API_KEY is missing. "
                "Please configure it in your .env file."
            )
        }]
    # Validate coordinates

    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):
        return [{
            "error": "Invalid latitude or longitude."
        }]
    # Validate facility type
    facility_type = facility_type.lower().strip()
    if facility_type not in FACILITY_TYPES:
        return [{
            "error": (
                "Unsupported facility type. Choose "
                "hospital, doctor, clinic, or pharmacy."
            )
        }]
    # Restrict search radius
    radius = max(
        1,
        min(int(radius), 50000)
    )
    category = FACILITY_TYPES[facility_type]
    # Geoapify Places API endpoint
    url = "https://api.geoapify.com/v2/places"
    # API parameters
    params = {
        "categories": category,
        "filter": (
            f"circle:{longitude},{latitude},{radius}"
        ),
        "bias": (
            f"proximity:{longitude},{latitude}"
        ),
        "limit": 10,
        "lang": "en",
        "apiKey": GEOAPIFY_API_KEY
    }
    # Call Geoapify API
    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else None
        )
        if status_code == 401 or status_code == 403:
            message = (
                "Geoapify API authentication failed. "
                "Check your API key and account settings."
            )
        elif status_code == 429:
            message = (
                "Geoapify API usage limit reached. "
                "Please try again later."
            )
        else:
            message = (
                f"Geoapify API returned an HTTP error: {status_code}."
            )
        return [{"error": message}]
    except requests.RequestException as error:
        return [{
            "error": f"Healthcare search failed: {error}"
        }]
    except ValueError:
        return [{
            "error": "Geoapify returned an invalid response."
        }]
    # Extract healthcare facilities
    features = data.get("features", [])
    results = []
    for feature in features:
        properties = feature.get("properties", {})
        place_lat = properties.get("lat")
        place_lon = properties.get("lon")
        distance = None
        if place_lat is not None and place_lon is not None:

            distance = round(
                calculate_distance_km(
                    latitude,
                    longitude,
                    place_lat,
                    place_lon
                ),
                2
            )
        # Build a map link when coordinates are available
        map_url = None
        if place_lat is not None and place_lon is not None:
            map_url = (
                "https://www.openstreetmap.org/"
                f"?mlat={place_lat}&mlon={place_lon}"
                f"#map=18/{place_lat}/{place_lon}"
            )
        results.append({
            "name": properties.get(
                "name",
                properties.get(
                    "address_line1",
                    "Unnamed healthcare facility"
                )
            ),
            "address": properties.get(
                "formatted",
                properties.get(
                    "address_line2",
                    "Address unavailable"
                )
            ),
            "distance_km": distance,
            "facility_type": facility_type,
            "categories": properties.get(
                "categories", []
            ),
            "maps_url": map_url
        })
    # Handle empty results
    if not results:
        return [{
            "message": (
                f"No {facility_type} facilities found "
                f"within {radius} metres."
            )
        }]
    return results