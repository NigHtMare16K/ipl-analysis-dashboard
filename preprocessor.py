from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "cricket_data_2025.csv"

NUMERIC_COLS = [
    "Matches_Batted",
    "Not_Outs",
    "Runs_Scored",
    "Batting_Average",
    "Balls_Faced",
    "Batting_Strike_Rate",
    "Centuries",
    "Half_Centuries",
    "Fours",
    "Sixes",
    "Catches_Taken",
    "Stumpings",
    "Matches_Bowled",
    "Balls_Bowled",
    "Runs_Conceded",
    "Wickets_Taken",
    "Bowling_Average",
    "Economy_Rate",
    "Bowling_Strike_Rate",
    "Four_Wicket_Hauls",
    "Five_Wicket_Hauls",
]


def preprocess() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    data.dropna(subset=["Year"], inplace=True)
    data["Year"] = data["Year"].astype(int)

    for col in NUMERIC_COLS:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    if data["Highest_Score"].dtype == "object":
        data["Highest_Score"] = (
            data["Highest_Score"]
            .astype(str)
            .str.replace("*", "", regex=False)
        )
        data["Highest_Score"] = pd.to_numeric(
            data["Highest_Score"], errors="coerce"
        ).fillna(0)

    data["Innings"] = (data["Matches_Batted"] - data["Not_Outs"]).clip(lower=0)
    return data
