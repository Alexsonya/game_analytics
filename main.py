#!/usr/bin/env python3
"""Game Analytics Console Application.

Parses game data, performs statistical analysis, and generates charts.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from parser import load_data, get_summary, get_top_games, get_numeric_columns
from analysis import (
    descriptive_stats, normality_test, ttest_two_genres, anova_genres,
    correlation_analysis, chi_square_test, mannwhitney_multiplayer,
)
from visualizer import ALL_CHARTS


def print_header(title: str):
    width = max(60, len(title) + 4)
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def print_section(title: str):
    print(f"\n--- {title} ---")


def choose_from_list(items: list[str], prompt: str = "Choose") -> str | None:
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    try:
        idx = int(input(f"\n{prompt} (number): ")) - 1
        if 0 <= idx < len(items):
            return items[idx]
    except (ValueError, EOFError):
        pass
    print("  Invalid choice.")
    return None


def menu_overview(df):
    print_header("DATASET OVERVIEW")
    print(get_summary(df))


def menu_top_games(df):
    print_header("TOP GAMES")
    col = choose_from_list(get_numeric_columns(df), "Sort by")
    if not col:
        return
    try:
        n = int(input("How many? [10]: ") or "10")
    except (ValueError, EOFError):
        n = 10
    print()
    top = get_top_games(df, by=col, n=n)
    print(top.to_string(index=False))


def menu_descriptive(df):
    print_header("DESCRIPTIVE STATISTICS")
    col = choose_from_list(get_numeric_columns(df), "Column")
    if col:
        print()
        print(descriptive_stats(df, col))


def menu_normality(df):
    print_header("NORMALITY TEST (Shapiro-Wilk)")
    col = choose_from_list(get_numeric_columns(df), "Column")
    if col:
        print()
        print(normality_test(df, col))


def menu_ttest(df):
    print_header("T-TEST: COMPARE TWO GENRES")
    genres = sorted(df["genre"].unique())
    print("\nFirst genre:")
    g1 = choose_from_list(genres)
    if not g1:
        return
    print("\nSecond genre:")
    g2 = choose_from_list(genres)
    if not g2:
        return
    col = choose_from_list(get_numeric_columns(df), "Compare by")
    if col:
        print()
        print(ttest_two_genres(df, g1, g2, col))


def menu_anova(df):
    print_header("ANOVA: COMPARE ALL GENRES")
    col = choose_from_list(get_numeric_columns(df), "Column")
    if col:
        print()
        print(anova_genres(df, col))


def menu_correlation(df):
    print_header("CORRELATION ANALYSIS")
    print("\nFirst variable:")
    c1 = choose_from_list(get_numeric_columns(df))
    if not c1:
        return
    print("\nSecond variable:")
    c2 = choose_from_list(get_numeric_columns(df))
    if not c2:
        return
    if c1 == c2:
        print("  Please choose two different variables.")
        return
    print()
    print(correlation_analysis(df, c1, c2))


def menu_chi_square(df):
    print_header("CHI-SQUARE TEST OF INDEPENDENCE")
    cat_cols = ["genre", "platform", "multiplayer", "in_app_purchases"]
    print("\nFirst variable:")
    c1 = choose_from_list(cat_cols)
    if not c1:
        return
    print("\nSecond variable:")
    c2 = choose_from_list(cat_cols)
    if not c2:
        return
    if c1 == c2:
        print("  Please choose two different variables.")
        return
    print()
    print(chi_square_test(df, c1, c2))


def menu_mannwhitney(df):
    print_header("MANN-WHITNEY U: MULTIPLAYER VS SINGLEPLAYER")
    col = choose_from_list(get_numeric_columns(df), "Compare by")
    if col:
        print()
        print(mannwhitney_multiplayer(df, col))


def menu_charts(df):
    print_header("CHART GENERATION")
    print("\n  0. Generate ALL charts")
    for key, (desc, _) in ALL_CHARTS.items():
        print(f"  {key}. {desc}")

    try:
        choice = input("\nChoice: ").strip()
    except EOFError:
        return

    if choice == "0":
        print("\nGenerating all charts...")
        for key, (desc, func) in ALL_CHARTS.items():
            path = func(df)
            print(f"  [{key}] {desc} -> {path}")
        print("\nAll charts saved!")
    elif choice in ALL_CHARTS:
        desc, func = ALL_CHARTS[choice]
        path = func(df)
        print(f"\n  Saved: {path}")
    else:
        print("  Invalid choice.")


def menu_fetch(df_holder: list):
    """Fetch real games from RAWG.io API."""
    print_header("FETCH GAMES FROM RAWG.IO")

    from fetcher import fetch_games, get_api_key
    saved_key = get_api_key()

    if saved_key:
        print(f"  API key found in .env: {saved_key[:8]}...")
    else:
        print("  No key in .env. Get one free at: https://rawg.io/apidocs")

    try:
        prompt = f"\n  API key [{'ENTER=use .env' if saved_key else 'required'}]: "
        api_key = input(prompt).strip() or saved_key
        if not api_key:
            print("  No API key provided.")
            return
        count = input("  Number of games to fetch [500]: ").strip()
        count = int(count) if count else 500
        year_from = input("  Year from [2010]: ").strip()
        year_from = int(year_from) if year_from else 2010
        year_to = input("  Year to [2025]: ").strip()
        year_to = int(year_to) if year_to else 2025
    except (ValueError, EOFError):
        print("  Invalid input.")
        return

    fetch_games(api_key, count=count, year_from=year_from, year_to=year_to)

    # Reload data
    df_holder[0] = load_data()
    print(f"\n  Reloaded: {len(df_holder[0])} games.")


def main():
    print_header("GAME ANALYTICS CONSOLE")
    print("  Loading dataset...")

    try:
        df = load_data()
    except FileNotFoundError:
        print("  Dataset not found. Generating sample data...")
        from generate_data import generate_dataset
        generate_dataset()
        df = load_data()

    print(f"  Loaded {len(df)} games.")
    print("  Tip: use option 11 to fetch real games from RAWG.io\n")

    # Mutable holder so fetch can replace the dataframe
    df_holder = [df]

    menu_items = [
        ("Dataset overview",                    lambda: menu_overview(df_holder[0])),
        ("Top games",                           lambda: menu_top_games(df_holder[0])),
        ("Descriptive statistics",              lambda: menu_descriptive(df_holder[0])),
        ("Normality test (Shapiro-Wilk)",       lambda: menu_normality(df_holder[0])),
        ("T-test: compare two genres",          lambda: menu_ttest(df_holder[0])),
        ("ANOVA: compare all genres",           lambda: menu_anova(df_holder[0])),
        ("Correlation analysis",                lambda: menu_correlation(df_holder[0])),
        ("Chi-square test",                     lambda: menu_chi_square(df_holder[0])),
        ("Mann-Whitney U: multi vs single",     lambda: menu_mannwhitney(df_holder[0])),
        ("Generate charts",                     lambda: menu_charts(df_holder[0])),
        (">> Fetch real games from RAWG.io",    lambda: menu_fetch(df_holder)),
    ]

    while True:
        print_section("MAIN MENU")
        for i, (label, _) in enumerate(menu_items, 1):
            print(f"  {i:2d}. {label}")
        print(f"   0. Exit")

        try:
            choice = int(input("\nChoice: "))
        except (ValueError, EOFError):
            print("  Invalid input.")
            continue

        if choice == 0:
            print("\nGoodbye!")
            break
        elif 1 <= choice <= len(menu_items):
            menu_items[choice - 1][1]()
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
