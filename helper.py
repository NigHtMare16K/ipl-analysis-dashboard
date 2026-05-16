import pandas as pd


def career_batting_stats(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("Player_Name").agg(
        runs=("Runs_Scored", "sum"),
        innings=("Innings", "sum"),
        balls=("Balls_Faced", "sum"),
        fours=("Fours", "sum"),
        sixes=("Sixes", "sum"),
        centuries=("Centuries", "sum"),
        half_centuries=("Half_Centuries", "sum"),
        highest=("Highest_Score", "max"),
        seasons=("Year", "nunique"),
    )
    grouped["average"] = grouped.apply(
        lambda r: r["runs"] / r["innings"] if r["innings"] > 0 else 0, axis=1
    )
    grouped["strike_rate"] = grouped.apply(
        lambda r: (r["runs"] / r["balls"] * 100) if r["balls"] > 0 else 0, axis=1
    )
    return grouped.round(2)


def career_bowling_stats(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("Player_Name").agg(
        wickets=("Wickets_Taken", "sum"),
        runs_conceded=("Runs_Conceded", "sum"),
        balls_bowled=("Balls_Bowled", "sum"),
        five_wickets=("Five_Wicket_Hauls", "sum"),
        four_wickets=("Four_Wicket_Hauls", "sum"),
        matches_bowled=("Matches_Bowled", "sum"),
    )
    grouped["economy"] = grouped.apply(
        lambda r: (r["runs_conceded"] / r["balls_bowled"] * 6)
        if r["balls_bowled"] > 0
        else 0,
        axis=1,
    )
    grouped["bowling_avg"] = grouped.apply(
        lambda r: r["runs_conceded"] / r["wickets"] if r["wickets"] > 0 else 0,
        axis=1,
    )
    return grouped.round(2)


def highest_runs(data: pd.DataFrame) -> pd.Series:
    return (
        data.groupby("Player_Name")["Runs_Scored"]
        .sum()
        .sort_values(ascending=False)
    )


def top_batters(data: pd.DataFrame, min_innings: int = 20) -> pd.DataFrame:
    stats = career_batting_stats(data)
    qualified = stats[stats["innings"] >= min_innings].sort_values(
        "runs", ascending=False
    )
    return qualified


def top_bowlers(data: pd.DataFrame, min_wickets: int = 20) -> pd.DataFrame:
    stats = career_bowling_stats(data)
    qualified = stats[stats["wickets"] >= min_wickets].sort_values(
        "wickets", ascending=False
    )
    return qualified


def all_rounders(data: pd.DataFrame, min_runs: int = 500, min_wickets: int = 30) -> pd.DataFrame:
    bat = career_batting_stats(data)[["runs"]]
    bowl = career_bowling_stats(data)[["wickets"]]
    merged = bat.join(bowl, how="inner")
    merged = merged[(merged["runs"] >= min_runs) & (merged["wickets"] >= min_wickets)]
    if merged.empty:
        return merged
    merged["score"] = (
        (merged["runs"] / merged["runs"].max()) * 50
        + (merged["wickets"] / merged["wickets"].max()) * 50
    ).round(1)
    return merged.sort_values("score", ascending=False)


def player_season_history(data: pd.DataFrame, player: str) -> pd.DataFrame:
    player_df = data[data["Player_Name"] == player].sort_values("Year")
    cols = [
        "Year",
        "Runs_Scored",
        "Wickets_Taken",
        "Batting_Average",
        "Batting_Strike_Rate",
        "Economy_Rate",
        "Matches_Batted",
        "Centuries",
        "Half_Centuries",
        "Sixes",
    ]
    return player_df[cols]


def player_career_summary(data: pd.DataFrame, player: str) -> dict:
    player_df = data[data["Player_Name"] == player]
    bat = career_batting_stats(player_df).loc[player]
    bowl = career_bowling_stats(player_df).loc[player]
    return {
        "seasons": int(player_df["Year"].nunique()),
        "runs": int(bat["runs"]),
        "wickets": int(bowl["wickets"]),
        "average": bat["average"],
        "strike_rate": bat["strike_rate"],
        "economy": bowl["economy"],
        "centuries": int(bat["centuries"]),
        "half_centuries": int(bat["half_centuries"]),
        "highest": int(bat["highest"]),
        "fours": int(bat["fours"]),
        "sixes": int(bat["sixes"]),
        "five_wickets": int(bowl["five_wickets"]),
    }


def season_summary(data: pd.DataFrame, year: int) -> dict:
    season = data[data["Year"] == year]
    active_batters = season[season["Runs_Scored"] > 0]
    active_bowlers = season[season["Wickets_Taken"] > 0]
    top_scorer = (
        active_batters.groupby("Player_Name")["Runs_Scored"]
        .sum()
        .idxmax()
        if not active_batters.empty
        else "N/A"
    )
    top_wicket = (
        active_bowlers.groupby("Player_Name")["Wickets_Taken"]
        .sum()
        .idxmax()
        if not active_bowlers.empty
        else "N/A"
    )
    return {
        "players": season["Player_Name"].nunique(),
        "total_runs": int(season["Runs_Scored"].sum()),
        "total_wickets": int(season["Wickets_Taken"].sum()),
        "total_sixes": int(season["Sixes"].sum()),
        "total_fours": int(season["Fours"].sum()),
        "centuries": int(season["Centuries"].sum()),
        "top_scorer": top_scorer,
        "top_wicket_taker": top_wicket,
    }


def runs_by_season(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby("Year")["Runs_Scored"]
        .sum()
        .reset_index()
        .rename(columns={"Runs_Scored": "Total_Runs"})
    )


def wickets_by_season(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby("Year")["Wickets_Taken"]
        .sum()
        .reset_index()
        .rename(columns={"Wickets_Taken": "Total_Wickets"})
    )


def power_hitters(data: pd.DataFrame, min_runs: int = 200) -> pd.DataFrame:
    stats = career_batting_stats(data)
    stats = stats[stats["runs"] >= min_runs].copy()
    stats["boundary_pct"] = (
        (stats["fours"] * 4 + stats["sixes"] * 6) / stats["runs"] * 100
    ).round(1)
    return stats.sort_values("sixes", ascending=False)[
        ["runs", "sixes", "fours", "boundary_pct", "strike_rate"]
    ]


def milestone_players(data: pd.DataFrame) -> pd.DataFrame:
    stats = career_batting_stats(data)
    return stats[stats["centuries"] > 0].sort_values(
        ["centuries", "runs"], ascending=False
    )[["runs", "centuries", "half_centuries", "highest"]]
