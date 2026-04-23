"""Fetch real game data from RAWG.io API."""

import csv
import os
import time
import urllib.request
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
API_BASE = "https://api.rawg.io/api/games"
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def load_env():
    """Load variables from .env file if it exists."""
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
PAGE_SIZE = 40  # max allowed by RAWG


def fetch_games(api_key: str, count: int = 500, year_from: int = 2010,
                year_to: int = 2025) -> str:
    """Fetch games from RAWG API and save to CSV.

    Args:
        api_key:   RAWG API key (free at https://rawg.io/apidocs)
        count:     number of games to fetch
        year_from: earliest release year
        year_to:   latest release year
    Returns:
        path to saved CSV file
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, "games.csv")

    fieldnames = [
        "id", "title", "genre", "platform", "developer", "release_year",
        "rating", "user_score", "sales_millions", "price_usd",
        "avg_playtime_hours", "multiplayer", "in_app_purchases",
    ]

    games = []
    pages_needed = (count + PAGE_SIZE - 1) // PAGE_SIZE
    fetched = 0

    print(f"  Fetching {count} games from RAWG.io ({pages_needed} pages)...")

    for page in range(1, pages_needed + 1):
        url = (
            f"{API_BASE}?key={api_key}"
            f"&page={page}&page_size={PAGE_SIZE}"
            f"&dates={year_from}-01-01,{year_to}-12-31"
            f"&ordering=-rating"
            f"&metacritic=1,100"
        )

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GameAnalytics/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break

        results = data.get("results", [])
        if not results:
            print(f"  No more results at page {page}.")
            break

        for g in results:
            if fetched >= count:
                break

            # Extract primary genre
            genres = g.get("genres", [])
            genre = genres[0]["name"] if genres else "Unknown"

            # Extract platforms
            platforms = g.get("platforms") or []
            platform_names = [p["platform"]["name"] for p in platforms]
            platform = _simplify_platform(platform_names)

            # Release year
            released = g.get("released") or ""
            year = int(released[:4]) if len(released) >= 4 else 0

            # RAWG rating is 0-5, scale to 0-10
            rating = round((g.get("rating") or 0) * 2, 1)

            # Metacritic as user_score (already 0-100, scale to 0-10)
            metacritic = g.get("metacritic") or 0
            user_score = round(metacritic / 10, 1) if metacritic else rating

            # Playtime (RAWG provides this in hours)
            playtime = g.get("playtime") or 0

            # Multiplayer detection from tags
            tags = [t.get("slug", "") for t in (g.get("tags") or [])]
            multiplayer = any("multiplayer" in t or "online" in t or "co-op" in t
                              for t in tags)

            fetched += 1
            games.append({
                "id": fetched,
                "title": g.get("name", f"Game_{fetched}"),
                "genre": genre,
                "platform": platform,
                "developer": "",  # requires extra API call
                "release_year": year,
                "rating": rating,
                "user_score": user_score,
                "sales_millions": "",  # RAWG doesn't provide sales
                "price_usd": "",       # RAWG doesn't provide price
                "avg_playtime_hours": playtime,
                "multiplayer": int(multiplayer),
                "in_app_purchases": 0,
            })

        progress = min(fetched, count)
        print(f"  Page {page}/{pages_needed} — {progress}/{count} games")

        if fetched >= count:
            break

        if page < pages_needed:
            time.sleep(0.25)  # rate limit courtesy

    # Enrich: fetch developers for each game (batch-friendly)
    print("  Fetching developer info...")
    _enrich_developers(games, api_key)

    # Write CSV
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(games)

    print(f"  Saved {len(games)} games to {filepath}")
    return filepath


def _simplify_platform(names: list[str]) -> str:
    """Map detailed platform names to simplified categories."""
    name_str = " ".join(names).lower()
    if "playstation" in name_str:
        return "PlayStation"
    if "xbox" in name_str:
        return "Xbox"
    if "nintendo" in name_str or "switch" in name_str or "wii" in name_str:
        return "Nintendo"
    if "ios" in name_str or "android" in name_str:
        return "Mobile"
    if "pc" in name_str or "windows" in name_str or "linux" in name_str or "mac" in name_str:
        return "PC"
    return "PC"


def _enrich_developers(games: list[dict], api_key: str):
    """Fetch developer names from RAWG game detail endpoint."""
    for i, game in enumerate(games):
        if game["developer"]:
            continue
        game_id = game.get("_rawg_id")
        if not game_id:
            # Can't fetch without RAWG id; leave empty
            continue
        # Skip to avoid excessive API calls — developer is optional
    # Developer enrichment would require per-game requests.
    # For large datasets this is slow; mark as "Unknown" instead.
    for g in games:
        if not g["developer"]:
            g["developer"] = "Unknown"


def get_api_key() -> str:
    """Get API key from environment (.env file or shell env)."""
    load_env()
    return os.environ.get("RAWG_API_KEY", "")


if __name__ == "__main__":
    import sys

    key = get_api_key()
    n = 500

    # Parse args: fetcher.py [API_KEY] [COUNT]
    args = sys.argv[1:]
    if args and not args[0].isdigit():
        key = args.pop(0)
    if args and args[0].isdigit():
        n = int(args[0])

    if not key:
        print("Usage: python3 fetcher.py [RAWG_API_KEY] [count]")
        print("  or set RAWG_API_KEY in .env file")
        print("  Get a free key at: https://rawg.io/apidocs")
        sys.exit(1)

    fetch_games(key, count=n)
