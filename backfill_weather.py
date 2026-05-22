"""
Run once to backfill historical data from Open-Meteo archive API.
Usage: python backfill_weather.py [days]   (default: 30)
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

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


def fetch_city_range(name, lat, lon, start_date, end_date):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily={DAILY_VARS}"
        f"&timezone=Europe%2FMadrid"
    )
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())

    d = data["daily"]
    result = {}
    for i, date in enumerate(d["time"]):
        result[date] = {
            "temp_max":       d["temperature_2m_max"][i],
            "temp_min":       d["temperature_2m_min"][i],
            "precipitation":  d["precipitation_sum"][i],
            "windspeed_max":  d["windspeed_10m_max"][i],
            "sunshine_hours": round((d["sunshine_duration"][i] or 0) / 3600, 1),
            "weathercode":    d["weathercode"][i],
        }
    return result


def load_history():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    today = datetime.now(timezone.utc).date()
    # Archive API has ~5-day lag; yesterday is the safe upper bound
    end = today - timedelta(days=1)
    start = end - timedelta(days=days - 1)

    history = load_history()
    existing_dates = {e["date"] for e in history}

    missing = [
        str(start + timedelta(days=i))
        for i in range(days)
        if str(start + timedelta(days=i)) not in existing_dates
    ]

    if not missing:
        print("No missing dates — nothing to backfill.")
        return

    print(f"Backfilling {len(missing)} missing dates: {missing[0]} to {missing[-1]}")

    # Fetch all cities for the full range in one request each
    city_data = {}
    for name, coords in CITIES.items():
        print(f"  Fetching {name}…")
        city_data[name] = fetch_city_range(
            name, coords["lat"], coords["lon"],
            str(start), str(end)
        )

    # Build new entries only for missing dates
    new_entries = []
    for date in missing:
        cities = {}
        for name in CITIES:
            if date in city_data[name]:
                cities[name] = city_data[name][date]
        new_entries.append({
            "date":       date,
            "fetched_at": f"{date}T00:00:00Z",
            "cities":     cities,
        })

    history.extend(new_entries)
    history.sort(key=lambda e: e["date"])
    save_history(history)
    print(f"Done. Added {len(new_entries)} entries. Total: {len(history)} days.")


if __name__ == "__main__":
    main()
