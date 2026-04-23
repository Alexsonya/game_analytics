"""Chart generation with matplotlib and seaborn."""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving to files

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "charts")


def _ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _save(fig, name: str) -> str:
    _ensure_dir()
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def rating_distribution(df: pd.DataFrame) -> str:
    """Histogram + KDE of critic ratings."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["rating"], bins=30, kde=True, ax=ax, color="steelblue")
    ax.set_title("Distribution of Critic Ratings", fontsize=14)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")
    ax.axvline(df["rating"].mean(), color="red", linestyle="--",
               label=f'Mean: {df["rating"].mean():.2f}')
    ax.legend()
    return _save(fig, "rating_distribution")


def sales_by_genre(df: pd.DataFrame) -> str:
    """Bar chart of average sales per genre."""
    fig, ax = plt.subplots(figsize=(10, 6))
    order = df.groupby("genre")["sales_millions"].mean().sort_values(ascending=False).index
    sns.barplot(data=df, x="genre", y="sales_millions", hue="genre",
                order=order, ax=ax, palette="viridis", errorbar="ci", legend=False)
    ax.set_title("Average Sales by Genre (with 95% CI)", fontsize=14)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Sales (millions)")
    ax.tick_params(axis="x", rotation=45)
    return _save(fig, "sales_by_genre")


def rating_boxplot_by_genre(df: pd.DataFrame) -> str:
    """Box plot of ratings by genre."""
    fig, ax = plt.subplots(figsize=(10, 6))
    order = df.groupby("genre")["rating"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="genre", y="rating", hue="genre",
                order=order, ax=ax, palette="Set2", legend=False)
    ax.set_title("Rating Distribution by Genre", fontsize=14)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Rating")
    ax.tick_params(axis="x", rotation=45)
    return _save(fig, "rating_boxplot_genre")


def price_vs_rating(df: pd.DataFrame) -> str:
    """Scatter plot: price vs rating, colored by genre."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x="price_usd", y="rating", hue="genre",
                    alpha=0.6, ax=ax)
    # Trend line
    z = np.polyfit(df["price_usd"], df["rating"], 1)
    p = np.poly1d(z)
    x_range = np.linspace(df["price_usd"].min(), df["price_usd"].max(), 100)
    ax.plot(x_range, p(x_range), "r--", linewidth=2, label="Trend")
    ax.set_title("Price vs Rating", fontsize=14)
    ax.set_xlabel("Price (USD)")
    ax.set_ylabel("Rating")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    return _save(fig, "price_vs_rating")


def yearly_trends(df: pd.DataFrame) -> str:
    """Line chart: average rating and sales over years."""
    yearly = df.groupby("release_year").agg(
        avg_rating=("rating", "mean"),
        avg_sales=("sales_millions", "mean"),
        count=("id", "count"),
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    color1 = "steelblue"
    ax1.plot(yearly["release_year"], yearly["avg_rating"], "o-",
             color=color1, linewidth=2, label="Avg Rating")
    ax1.set_xlabel("Release Year")
    ax1.set_ylabel("Average Rating", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)

    ax2 = ax1.twinx()
    color2 = "coral"
    ax2.bar(yearly["release_year"], yearly["count"], alpha=0.3,
            color=color2, label="Number of Games")
    ax2.set_ylabel("Number of Games", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)

    fig.suptitle("Yearly Trends: Rating & Game Count", fontsize=14)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    return _save(fig, "yearly_trends")


def correlation_heatmap(df: pd.DataFrame) -> str:
    """Heatmap of correlations between numeric columns."""
    numeric_cols = ["rating", "user_score", "sales_millions", "price_usd",
                    "avg_playtime_hours", "release_year"]
    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, ax=ax, square=True)
    ax.set_title("Correlation Matrix", fontsize=14)
    return _save(fig, "correlation_heatmap")


def multiplayer_comparison(df: pd.DataFrame) -> str:
    """Violin plot: sales for multiplayer vs singleplayer."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    df_plot = df.copy()
    df_plot["mode"] = df_plot["multiplayer"].map({True: "Multiplayer", False: "Singleplayer"})

    sns.violinplot(data=df_plot, x="mode", y="sales_millions", hue="mode",
                   ax=axes[0], palette=["#ff7f0e", "#1f77b4"], legend=False)
    axes[0].set_title("Sales: Multiplayer vs Singleplayer")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Sales (millions)")

    sns.violinplot(data=df_plot, x="mode", y="rating", hue="mode",
                   ax=axes[1], palette=["#ff7f0e", "#1f77b4"], legend=False)
    axes[1].set_title("Ratings: Multiplayer vs Singleplayer")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Rating")

    fig.suptitle("Multiplayer vs Singleplayer Comparison", fontsize=14)
    fig.tight_layout()
    return _save(fig, "multiplayer_comparison")


def platform_genre_heatmap(df: pd.DataFrame) -> str:
    """Heatmap: number of games per platform-genre pair."""
    ct = pd.crosstab(df["platform"], df["genre"])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(ct, annot=True, fmt="d", cmap="YlOrRd", ax=ax)
    ax.set_title("Game Count: Platform x Genre", fontsize=14)
    return _save(fig, "platform_genre_heatmap")


ALL_CHARTS = {
    "1": ("Rating distribution (histogram + KDE)", rating_distribution),
    "2": ("Average sales by genre (bar chart)", sales_by_genre),
    "3": ("Ratings by genre (box plot)", rating_boxplot_by_genre),
    "4": ("Price vs Rating (scatter)", price_vs_rating),
    "5": ("Yearly trends (line chart)", yearly_trends),
    "6": ("Correlation heatmap", correlation_heatmap),
    "7": ("Multiplayer vs Singleplayer (violin plot)", multiplayer_comparison),
    "8": ("Platform x Genre (heatmap)", platform_genre_heatmap),
}
