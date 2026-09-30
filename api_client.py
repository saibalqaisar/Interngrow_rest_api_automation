"""Consume public REST APIs (no API key needed) and parse JSON."""
from utils import safe_get, log

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def get_weather(city):
    """City name -> coordinates -> current weather. Returns dict or None."""
    geo = safe_get(GEO_URL, {"name": city, "count": 1})
    if not geo:
        return None
    results = geo.json().get("results")
    if not results:
        log.warning("City not found: %s", city)
        return None
    place = results[0]

    resp = safe_get(WEATHER_URL, {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    })
    if not resp:
        return None
    cur = resp.json()["current"]
    return {
        "city": place["name"],
        "country": place.get("country", ""),
        "temperature_c": cur["temperature_2m"],
        "humidity_pct": cur["relative_humidity_2m"],
        "wind_kmh": cur["wind_speed_10m"],
    }


def get_news(limit=5):
    """Top Hacker News stories. Returns list of {title, url}."""
    resp = safe_get(HN_TOP)
    if not resp:
        return []
    stories = []
    for story_id in resp.json()[:limit]:
        item = safe_get(HN_ITEM.format(story_id))
        if item:
            data = item.json()
            stories.append({
                "title": data.get("title", "No title"),
                "url": data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            })
    return stories
