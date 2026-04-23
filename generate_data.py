"""Generate a realistic game dataset for analysis."""

import csv
import random
import os

random.seed(42)

GENRES = ["Action", "RPG", "Strategy", "Shooter", "Adventure", "Sports", "Puzzle", "Simulation"]
PLATFORMS = ["PC", "PlayStation", "Xbox", "Nintendo", "Mobile"]
DEVELOPERS = [
    "Ubisoft", "EA", "Valve", "CD Projekt", "Rockstar", "Bethesda",
    "Blizzard", "Epic Games", "Capcom", "Square Enix", "Bandai Namco",
    "Naughty Dog", "Insomniac", "FromSoftware", "Nintendo EPD",
    "Supergiant", "Team Cherry", "Re-Logic", "ConcernedApe", "Larian Studios",
]


def generate_rating(genre: str, year: int) -> float:
    """Rating depends on genre and has a slight upward trend over years."""
    base = {"RPG": 7.5, "Action": 7.0, "Strategy": 7.2, "Shooter": 6.8,
            "Adventure": 7.3, "Sports": 6.5, "Puzzle": 7.0, "Simulation": 6.9}
    r = base[genre] + random.gauss(0, 1.2) + (year - 2015) * 0.02
    return round(max(1.0, min(10.0, r)), 1)


def generate_sales(rating: float, genre: str) -> float:
    """Sales correlate with rating; shooters and action sell more."""
    multiplier = {"Shooter": 1.4, "Action": 1.3, "RPG": 1.1, "Sports": 1.2,
                  "Adventure": 0.9, "Strategy": 0.8, "Puzzle": 0.6, "Simulation": 0.7}
    sales = (rating ** 1.5) * multiplier[genre] * random.uniform(0.3, 2.5)
    return round(max(0.01, sales), 2)


def generate_price(genre: str) -> float:
    base = {"RPG": 49.99, "Action": 59.99, "Strategy": 39.99, "Shooter": 59.99,
            "Adventure": 39.99, "Sports": 59.99, "Puzzle": 14.99, "Simulation": 29.99}
    price = base[genre] + random.gauss(0, 10)
    return round(max(4.99, min(69.99, price)), 2)


def generate_playtime(genre: str) -> float:
    base = {"RPG": 60, "Action": 25, "Strategy": 45, "Shooter": 30,
            "Adventure": 20, "Sports": 40, "Puzzle": 15, "Simulation": 50}
    hours = base[genre] + random.gauss(0, base[genre] * 0.4)
    return round(max(2, hours), 1)


def generate_dataset(n: int = 500) -> str:
    filepath = os.path.join(os.path.dirname(__file__), "data", "games.csv")
    fieldnames = [
        "id", "title", "genre", "platform", "developer", "release_year",
        "rating", "user_score", "sales_millions", "price_usd",
        "avg_playtime_hours", "multiplayer", "in_app_purchases",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, n + 1):
            genre = random.choice(GENRES)
            year = random.randint(2010, 2025)
            rating = generate_rating(genre, year)
            price = generate_price(genre)

            # user_score slightly differs from critic rating
            user_score = round(max(1.0, min(10.0, rating + random.gauss(-0.3, 0.8))), 1)

            multiplayer = genre in ("Shooter", "Sports", "Action") or random.random() < 0.2
            iap = genre in ("Sports", "Mobile") or random.random() < 0.15

            writer.writerow({
                "id": i,
                "title": f"Game_{i:04d}",
                "genre": genre,
                "platform": random.choice(PLATFORMS),
                "developer": random.choice(DEVELOPERS),
                "release_year": year,
                "rating": rating,
                "user_score": user_score,
                "sales_millions": generate_sales(rating, genre),
                "price_usd": price,
                "avg_playtime_hours": generate_playtime(genre),
                "multiplayer": int(multiplayer),
                "in_app_purchases": int(iap),
            })

    return filepath


if __name__ == "__main__":
    path = generate_dataset()
    print(f"Dataset generated: {path}")
