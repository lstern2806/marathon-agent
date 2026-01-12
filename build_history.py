import json
import pandas as pd
from load_data import load_strava_activities

CSV_PATH = "data/activities.csv"
OUT_PATH = "runner_history.json"

def to_miles(distance_series: pd.Series) -> pd.Series:
    s = pd.to_numeric(distance_series, errors="coerce")
    med = s.dropna().median()
    if pd.isna(med):
        return s
    if med > 1000:  # meters
        return s / 1609.34
    return s  # assume miles

def parse_seconds(series: pd.Series) -> pd.Series:
    # Strava can be hh:mm:ss (string) or seconds (numeric)
    if series.dtype == object:
        return pd.to_timedelta(series, errors="coerce").dt.total_seconds()
    return pd.to_numeric(series, errors="coerce")

def main():
    df = load_strava_activities(CSV_PATH)

    # Keep runs only
    if "Activity Type" in df.columns:
        df = df[df["Activity Type"].isin(["Run", "Virtual Run"])].copy()

    # Dates
    df["Activity Date"] = pd.to_datetime(df["Activity Date"], errors="coerce")
    df = df.dropna(subset=["Activity Date"]).copy()

    # Distance + time
    df["distance_mi"] = to_miles(df["Distance"]) if "Distance" in df.columns else pd.NA
    if "Moving Time" in df.columns:
        df["moving_seconds"] = parse_seconds(df["Moving Time"])
    elif "Elapsed Time" in df.columns:
        df["moving_seconds"] = parse_seconds(df["Elapsed Time"])
    else:
        df["moving_seconds"] = pd.NA

    df = df.dropna(subset=["distance_mi"]).copy()
    df = df[df["distance_mi"] > 0].copy()

    # Pace
    df["pace_min_per_mi"] = pd.NA
    m = df["moving_seconds"].notna()
    df.loc[m, "pace_min_per_mi"] = (df.loc[m, "moving_seconds"] / 60.0) / df.loc[m, "distance_mi"]

    # Weekly mileage trend (last 16 weeks)
    df["week_start"] = df["Activity Date"].dt.to_period("W-MON").dt.start_time.dt.date
    weekly = df.groupby("week_start")["distance_mi"].sum().sort_index().tail(16)

    # Recent pace band (middle 60% of last 8 weeks)
    recent = df[df["Activity Date"] >= (df["Activity Date"].max() - pd.Timedelta(days=56))].copy()
    valid_paces = pd.to_numeric(recent["pace_min_per_mi"], errors="coerce").dropna()
    pace_band = None
    if len(valid_paces) >= 5:
        pace_band = {
            "p20": round(float(valid_paces.quantile(0.2)), 2),
            "p50": round(float(valid_paces.quantile(0.5)), 2),
            "p80": round(float(valid_paces.quantile(0.8)), 2)
        }

    # Best efforts (recent)
    def best_effort(min_mi, max_mi):
        c = recent[(recent["distance_mi"] >= min_mi) & (recent["distance_mi"] <= max_mi)].copy()
        c["pace_min_per_mi"] = pd.to_numeric(c["pace_min_per_mi"], errors="coerce")
        c = c.dropna(subset=["pace_min_per_mi"])
        if len(c) == 0:
            return None
        best = c.sort_values("pace_min_per_mi").iloc[0]
        return {
            "date": str(best["Activity Date"].date()),
            "distance_mi": round(float(best["distance_mi"]), 2),
            "pace_min_per_mi": round(float(best["pace_min_per_mi"]), 2),
            "activity_name": str(best.get("Activity Name", ""))[:80]
        }

    history = {
        "generated_at": pd.Timestamp.now().isoformat(timespec="seconds"),
        "runs_count_total": int(len(df)),
        "date_range": {
            "start": str(df["Activity Date"].min().date()),
            "end": str(df["Activity Date"].max().date())
        },
        "weekly_mileage_last_16_weeks": [
            {"week_start": str(k), "miles": round(float(v), 2)}
            for k, v in weekly.items()
        ],
        "pace_band_last_8_weeks_min_per_mile": pace_band,
        "best_efforts_last_8_weeks": {
            "best_1_mileish": best_effort(0.8, 1.3),
            "best_5kish": best_effort(2.5, 4.0),
            "best_10kish": best_effort(5.5, 7.0)
        }
    }

    with open(OUT_PATH, "w") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()

