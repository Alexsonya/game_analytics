"""Statistical analysis: hypothesis tests, correlations, descriptive stats."""

import numpy as np
import pandas as pd
from scipy import stats


def descriptive_stats(df: pd.DataFrame, column: str) -> str:
    """Descriptive statistics for a numeric column."""
    s = df[column]
    lines = [
        f"  Column:    {column}",
        f"  Count:     {s.count()}",
        f"  Mean:      {s.mean():.4f}",
        f"  Median:    {s.median():.4f}",
        f"  Std dev:   {s.std():.4f}",
        f"  Min:       {s.min():.4f}",
        f"  Max:       {s.max():.4f}",
        f"  Skewness:  {s.skew():.4f}",
        f"  Kurtosis:  {s.kurtosis():.4f}",
    ]
    return "\n".join(lines)


def normality_test(df: pd.DataFrame, column: str) -> str:
    """Shapiro-Wilk test for normality."""
    data = df[column].dropna()
    # Shapiro-Wilk works best on samples up to 5000
    sample = data.sample(min(len(data), 5000), random_state=42)
    stat, p_value = stats.shapiro(sample)

    result = "normally distributed" if p_value > 0.05 else "NOT normally distributed"
    lines = [
        f"  Shapiro-Wilk test for '{column}'",
        f"  Statistic: {stat:.6f}",
        f"  p-value:   {p_value:.6f}",
        f"  Result:    Data is {result} (alpha=0.05)",
    ]
    return "\n".join(lines)


def ttest_two_genres(df: pd.DataFrame, genre1: str, genre2: str,
                     column: str = "rating") -> str:
    """Independent t-test: compare a metric between two genres."""
    g1 = df[df["genre"] == genre1][column].dropna()
    g2 = df[df["genre"] == genre2][column].dropna()

    if len(g1) < 2 or len(g2) < 2:
        return "  Not enough data for at least one of the genres."

    stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)
    sig = "YES (reject H0)" if p_value < 0.05 else "NO (fail to reject H0)"

    lines = [
        f"  Independent t-test: {genre1} vs {genre2} ({column})",
        f"  {genre1}: mean={g1.mean():.3f}, n={len(g1)}",
        f"  {genre2}: mean={g2.mean():.3f}, n={len(g2)}",
        f"  t-statistic: {stat:.4f}",
        f"  p-value:     {p_value:.6f}",
        f"  Significant: {sig}",
    ]
    return "\n".join(lines)


def anova_genres(df: pd.DataFrame, column: str = "rating") -> str:
    """One-way ANOVA: compare a metric across all genres."""
    groups = [group[column].dropna().values for _, group in df.groupby("genre")]
    stat, p_value = stats.f_oneway(*groups)
    sig = "YES (reject H0)" if p_value < 0.05 else "NO (fail to reject H0)"

    genre_means = df.groupby("genre")[column].mean().sort_values(ascending=False)
    means_str = "\n".join(f"    {g}: {m:.3f}" for g, m in genre_means.items())

    lines = [
        f"  One-way ANOVA for '{column}' across genres",
        f"  F-statistic: {stat:.4f}",
        f"  p-value:     {p_value:.6f}",
        f"  Significant: {sig}",
        f"  Group means:",
        means_str,
    ]
    return "\n".join(lines)


def correlation_analysis(df: pd.DataFrame, col1: str, col2: str) -> str:
    """Pearson and Spearman correlation between two columns."""
    data = df[[col1, col2]].dropna()

    pearson_r, pearson_p = stats.pearsonr(data[col1], data[col2])
    spearman_r, spearman_p = stats.spearmanr(data[col1], data[col2])

    def interpret(r: float) -> str:
        ar = abs(r)
        if ar < 0.1:
            return "negligible"
        if ar < 0.3:
            return "weak"
        if ar < 0.5:
            return "moderate"
        if ar < 0.7:
            return "strong"
        return "very strong"

    lines = [
        f"  Correlation: {col1} vs {col2} (n={len(data)})",
        f"",
        f"  Pearson:  r={pearson_r:.4f}, p={pearson_p:.6f} ({interpret(pearson_r)})",
        f"  Spearman: r={spearman_r:.4f}, p={spearman_p:.6f} ({interpret(spearman_r)})",
    ]
    return "\n".join(lines)


def chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> str:
    """Chi-square test of independence between two categorical variables."""
    contingency = pd.crosstab(df[col1], df[col2])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    sig = "YES (reject H0)" if p_value < 0.05 else "NO (fail to reject H0)"

    # Cramer's V
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

    lines = [
        f"  Chi-square test: {col1} vs {col2}",
        f"  Chi2:      {chi2:.4f}",
        f"  p-value:   {p_value:.6f}",
        f"  DoF:       {dof}",
        f"  Cramer's V: {cramers_v:.4f}",
        f"  Significant: {sig}",
    ]
    return "\n".join(lines)


def mannwhitney_multiplayer(df: pd.DataFrame, column: str = "sales_millions") -> str:
    """Mann-Whitney U test: multiplayer vs singleplayer games."""
    multi = df[df["multiplayer"]][column].dropna()
    single = df[~df["multiplayer"]][column].dropna()

    stat, p_value = stats.mannwhitneyu(multi, single, alternative="two-sided")
    sig = "YES (reject H0)" if p_value < 0.05 else "NO (fail to reject H0)"

    lines = [
        f"  Mann-Whitney U test: multiplayer vs singleplayer ({column})",
        f"  Multiplayer:   median={multi.median():.3f}, n={len(multi)}",
        f"  Singleplayer:  median={single.median():.3f}, n={len(single)}",
        f"  U-statistic:   {stat:.1f}",
        f"  p-value:       {p_value:.6f}",
        f"  Significant:   {sig}",
    ]
    return "\n".join(lines)
