"""Weather + News dashboard: builds a text report and saves JSON."""
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from api_client import get_weather, get_news
from scraper import scrape_quotes

load_dotenv()


def build_dashboard(city=None):
    city = city or os.getenv("CITY", "Lahore")
    weather, news, quotes = get_weather(city), get_news(5), scrape_quotes(3)

    lines = [f"=== DAILY DASHBOARD - {datetime.now():%d %b %Y %H:%M} ===", ""]
    if weather:
        lines += [
            f"Weather in {weather['city']}, {weather['country']}",
            f"  Temperature: {weather['temperature_c']} C",
            f"  Humidity:    {weather['humidity_pct']} %",
            f"  Wind:        {weather['wind_kmh']} km/h",
        ]
    else:
        lines.append("Weather: unavailable")
    lines += ["", "Top News:"]
    lines += [f"  {i}. {n['title']}\n     {n['url']}" for i, n in enumerate(news, 1)] or ["  unavailable"]
    lines += ["", "Quotes of the day:"]
    lines += [f"  \"{q['text']}\" - {q['author']}" for q in quotes] or ["  unavailable"]

    with open("dashboard.json", "w", encoding="utf-8") as f:
        json.dump({"weather": weather, "news": news, "quotes": quotes}, f, indent=2)
    return "\n".join(lines)
