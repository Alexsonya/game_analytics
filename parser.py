"""Data loading, validation, and preprocessing."""

import pandas as pd
import os


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "games.csv")

ALL_NUMERIC = ["rating", "user_score", "sales_millions", "price_usd", "avg_playtime_hours"]


def load_data(filepath: str = DATA_PATH) -> pd.DataFrame:
    """Load and validate the games dataset."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. Run: python generate_data.py"
        )

    df = pd.read_csv(filepath)

    # Convert numeric columns (empty strings -> NaN)
    for col in ALL_NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert booleans
    df["multiplayer"] = df["multiplayer"].astype(bool)
    df["in_app_purchases"] = df["in_app_purchases"].astype(bool)
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").fillna(0).astype(int)

    return df


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return numeric columns that actually have data (>50% non-null)."""
    available = []
    for col in ALL_NUMERIC:
        if col in df.columns and df[col].notna().mean() > 0.5:
            available.append(col)
    return available


def get_summary(df: pd.DataFrame) -> str:
    """Return a human-readable summary of the dataset."""
    lines = [
        f"  Records:        {len(df)}",
        f"  Genres:         {', '.join(sorted(df['genre'].unique()))}",
        f"  Platforms:      {', '.join(sorted(df['platform'].unique()))}",
        f"  Year range:     {df['release_year'].min()} - {df['release_year'].max()}",
    ]

    for col, label, fmt in [
        ("rating",            "Avg rating",     "{:.2f}"),
        ("user_score",        "Avg user score", "{:.2f}"),
        ("price_usd",         "Avg price",      "${:.2f}"),
        ("sales_millions",    "Avg sales",      "{:.2f}M copies"),
        ("avg_playtime_hours","Avg playtime",   "{:.1f} hours"),
    ]:
        if col in df.columns and df[col].notna().any():
            lines.append(f"  {label + ':':<18}{fmt.format(df[col].mean())}")

    lines.append(
        f"  {'Multiplayer:':<18}{df['multiplayer'].sum()} games "
        f"({df['multiplayer'].mean()*100:.1f}%)"
    )
    return "\n".join(lines)


def filter_by_genre(df: pd.DataFrame, genre: str) -> pd.DataFrame:
    return df[df["genre"] == genre]


def filter_by_platform(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    return df[df["platform"] == platform]


def filter_by_years(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    return df[(df["release_year"] >= start) & (df["release_year"] <= end)]


def get_top_games(df: pd.DataFrame, by: str = "rating", n: int = 10) -> pd.DataFrame:
    return df.nlargest(n, by)[["title", "genre", "platform", "release_year", by]]
