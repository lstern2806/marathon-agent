import pandas as pd
from load_data import load_strava_activities

def to_miles(distance_series: pd.Series) -> pd.Series:
    s = pd.to_numeric(distance_series, errors="coerce")
    med = s.dropna().median()
    if pd.isna(med):
        return s
    # If typical distances are huge, assume meters and convert to miles
    if med > 1000:
        return s / 1609.34
    return s  # assume already miles

def summarize_runs(df: pd.DataFrame, days_back: int = 56) -> dict:
    if "Activity Date" not in df.columns:
        raise ValueError("Missing Activity Date column after parsing.")

    df = df.dropna(subset=["Activity Date"]).copy()
    most_recent = df["Activity Date"].max()
    recent = df[df["Activity Date"] >= (most_recent - pd.Timedelta(days=days_back))].copy()

    # Filter to runs if column exists
    if "Activity Type" in recent.columns:
        recent = recent[recent["Activity Type"].isin(["Run", "Virtual Run"])].copy()

    if "Distance" not in recent.columns:
        raise ValueError("No Distance column found in Strava CSV.")

    recent["distance_mi"] = to_miles(recent["Distance"])
    recent["week"] = recent["Activity Date"].dt.to_period("W").astype(str)

    weekly_miles = recent.groupby("week")["distance_mi"].sum().sort_index()
    last_4 = weekly_miles.tail(4)

    total_miles = float(recent["distance_mi"].sum())
    runs_count = int(recent["distance_mi"].count())
    avg_weekly = float(last_4.mean()) if len(last_4) else 0.0
    max_week = float(weekly_miles.max()) if len(weekly_miles) else 0.0
    last_week = float(weekly_miles.iloc[-1]) if len(weekly_miles) else 0.0

    return {
        "days_back": days_back,
        "runs_count": runs_count,
        "total_miles": round(total_miles, 2),
        "avg_weekly_miles_last_4_weeks": round(avg_weekly, 2),
        "max_weekly_miles": round(max_week, 2),
        "last_week_miles": round(last_week, 2),
    }

if __name__ == "__main__":
    df = load_strava_activities("data/activities.csv")
    print(summarize_runs(df))

