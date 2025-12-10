from datetime import date

import requests


def get_user_location():
    """Detect user's city and coordinates using ipinfo.io (more reliable)."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5)
        data = r.json()

        # ipinfo returns "loc" as "lat,lon"
        loc = data.get("loc", "41.0082,28.9784").split(",")
        lat, lon = float(loc[0]), float(loc[1])

        city = data.get("city", "Istanbul")
        country = data.get("country", "TR")

        return {
            "city": city,
            "country": country,
            "lat": lat,
            "lon": lon
        }

    except Exception as e:
        print(f"⚠️ Fallback to Istanbul due to: {e}")
        return {"city": "Istanbul", "country": "TR", "lat": 41.0082, "lon": 28.9784}


def get_real_outdoor_temp(lat, lon):
    """Fetch real outdoor temperature using Open-Meteo (no API key required)."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m"
        )
        r = requests.get(url, timeout=5)
        data = r.json()
        return data["current"]["temperature_2m"]
    except Exception as e:
        print(f"⚠️ Weather API failed: {e}")
        raise


def get_real_indoor_temp():
    """Simulate sensor not connected — raises error."""
    raise ConnectionError("Indoor temperature sensor not available")


def get_real_energy_usage():
    """Simulate energy sensor not connected — raises error."""
    raise ConnectionError("Energy meter not available")


def get_if_weekend():

    NINJAS_KEY="Uroj2S9uJqDd9GWjr8XD8A==Ms2aycJifwN6JYIj"
    if not NINJAS_KEY:
        raise RuntimeError("API_NINJAS_KEY not set")

    try:
        loc = get_user_location()
        country = loc.get("country", "TR")

        today = date.today().isoformat()

        url = "https://api.api-ninjas.com/v1/isworkingday"
        params = {
            "country": country,
            "date": today
        }

        headers = {
            "X-Api-Key": NINJAS_KEY
        }

        r = requests.get(url, headers=headers, params=params, timeout=5)
        r.raise_for_status()

        data = r.json()

        # is_workday == False → weekend OR public holiday
        return not data.get("is_workday", True)

    except Exception as e:
        print(f"⚠️ isworkingday API failed: {e}")
        return False
