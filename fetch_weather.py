import json
import os
import urllib.request
from datetime import datetime, timezone

CITIES = {
    "Madrid":    {"lat": 40.4168, "lon": -3.7038},
    "Barcelona": {"lat": 41.3851, "lon":  2.1734},
    "Valencia":  {"lat": 39.4699, "lon": -0.3763},
    "Sevilla":   {"lat": 37.3891, "lon": -5.9845},
    "Bilbao":    {"lat": 43.2630, "lon": -2.9350},
    "Zaragoza":  {"lat": 41.6488, "lon": -0.8891},
}

DAILY_VARS = ",".join([
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
    "sunshine_duration",
    "weathercode",
])

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "weather.json")


def fetch_city(name, lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily={DAILY_VARS}"
        f"&timezone=Europe%2FMadrid"
        f"&forecast_days=1"
    )
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())

    d = data["daily"]
    return {
        "temp_max":        d["temperature_2m_max"][0],
        "temp_min":        d["temperature_2m_min"][0],
        "precipitation":   d["precipitation_sum"][0],
        "windspeed_max":   d["windspeed_10m_max"][0],
        "sunshine_hours":  round(d["sunshine_duration"][0] / 3600, 1),
        "weathercode":     d["weathercode"][0],
    }


def load_history():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    history = load_history()

    if any(entry["date"] == today for entry in history):
        print(f"Entry for {today} already exists — skipping.")
        return

    cities_data = {}
    for name, coords in CITIES.items():
        print(f"Fetching {name}...")
        cities_data[name] = fetch_city(name, coords["lat"], coords["lon"])

    history.append({
        "date":       today,
        "fetched_at": fetched_at,
        "cities":     cities_data,
    })

    save_history(history)
    print(f"Saved entry for {today} ({len(CITIES)} cities).")


if __name__ == "__main__":
    main()
