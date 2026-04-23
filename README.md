# Game Analytics

Console application for video game data analysis with statistical tests and chart generation.

## Features

- **Data parsing** — fetch real game data from [RAWG.io](https://rawg.io) API (or use built-in sample data)
- **Descriptive statistics** — mean, median, std, skewness, kurtosis
- **Hypothesis testing:**
  - Shapiro-Wilk normality test
  - Independent t-test (compare two genres)
  - One-way ANOVA (compare all genres)
  - Mann-Whitney U (multiplayer vs singleplayer)
  - Chi-square test of independence
- **Correlation analysis** — Pearson & Spearman
- **8 chart types** — histograms, bar charts, box plots, scatter plots, heatmaps, violin plots, trend lines

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/game_analytics.git
cd game_analytics
pip install -r requirements.txt
```

## API Key (optional)

To fetch real game data, get a free API key at https://rawg.io/apidocs, then:

```bash
cp .env.example .env
# edit .env and paste your key
```

## Usage

```bash
python3 main.py
```

Without an API key the app generates a sample dataset (500 games) on first launch.

To fetch real data, use menu option **11** or run directly:

```bash
python3 fetcher.py 1000        # fetches 1000 games (key from .env)
python3 fetcher.py YOUR_KEY 500 # pass key as argument
```

Charts are saved to `charts/` as PNG files.

## Project Structure

```
game_analytics/
├── main.py            # Console menu (entry point)
├── fetcher.py         # RAWG.io API data fetcher
├── parser.py          # Data loading & preprocessing
├── analysis.py        # Statistical tests
├── visualizer.py      # Chart generation
├── generate_data.py   # Sample data generator (fallback)
├── requirements.txt
├── .env.example       # API key template
└── data/
    └── games.csv      # Dataset (generated or fetched)
```
