import pandas as pd

def load_strava_activities(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalize date column
    if "Activity Date" in df.columns:
        df["Activity Date"] = pd.to_datetime(df["Activity Date"], errors="coerce")
    else:
        # Try to find any column containing "Date"
        date_cols = [c for c in df.columns if "Date" in c]
        if not date_cols:
            raise ValueError("No date column found in Strava CSV.")
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
        df = df.rename(columns={date_cols[0]: "Activity Date"})

    # Normalize type column (optional)
    if "Activity Type" in df.columns:
        df["Activity Type"] = df["Activity Type"].astype(str)

    return df



