import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import preprocessor
import helper

st.set_page_config(
    layout="wide",
    page_title="IPL Analytics",
    page_icon="🏏",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    return preprocessor.preprocess()


data = load_data()
years = sorted(data["Year"].unique())

st.sidebar.title("IPL Analytics")
st.sidebar.caption(f"Seasons {years[0]}–{years[-1]} · {data['Player_Name'].nunique()} players")

user_menu = st.sidebar.radio(
    "Navigate",
    (
        "Home",
        "Leaderboard",
        "Player Analysis",
        "Season Analysis",
        "Compare Players",
        "Insights",
    ),
)

# ── Home ──────────────────────────────────────────────────────────────────────
if user_menu == "Home":
    st.title("IPL Data Analysis Dashboard")
    st.markdown(
        "Explore player careers, season trends, and IPL records from "
        f"**{years[0]}** through **{years[-1]}**."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Players", data["Player_Name"].nunique())
    c2.metric("Seasons", len(years))
    c3.metric("Player-Seasons", f"{data.shape[0]:,}")
    c4.metric("Total Runs", f"{int(data['Runs_Scored'].sum()):,}")
    c5.metric("Total Wickets", f"{int(data['Wickets_Taken'].sum()):,}")

    col_a, col_b = st.columns(2)
    with col_a:
        runs_df = helper.runs_by_season(data)
        fig = px.bar(
            runs_df,
            x="Year",
            y="Total_Runs",
            title="Total Runs per Season",
            color_discrete_sequence=["#FF6B35"],
        )
        fig.update_layout(margin=dict(t=40, b=20), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        wk_df = helper.wickets_by_season(data)
        fig = px.bar(
            wk_df,
            x="Year",
            y="Total_Wickets",
            title="Total Wickets per Season",
            color_discrete_sequence=["#004E89"],
        )
        fig.update_layout(margin=dict(t=40, b=20), height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Dataset Preview")
    st.dataframe(data, use_container_width=True, height=320)

# ── Leaderboard ───────────────────────────────────────────────────────────────
elif user_menu == "Leaderboard":
    st.title("Leaderboards")
    st.markdown("Career aggregates with optional qualification filters.")

    tab_runs, tab_bowl, tab_all, tab_power, tab_mile = st.tabs(
        ["Run Scorers", "Wicket Takers", "All-Rounders", "Power Hitters", "Centuries"]
    )

    with tab_runs:
        min_inn = st.slider("Minimum innings (career)", 5, 50, 20, key="lb_inn")
        top = helper.top_batters(data, min_inn).head(15)
        fig = px.bar(
            top.reset_index(),
            x="runs",
            y="Player_Name",
            orientation="h",
            title=f"Top Run Scorers (min {min_inn} innings)",
            labels={"runs": "Runs", "Player_Name": ""},
            color="runs",
            color_continuous_scale="Oranges",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            top[["runs", "innings", "average", "strike_rate", "seasons"]],
            use_container_width=True,
        )

    with tab_bowl:
        min_wk = st.slider("Minimum wickets (career)", 5, 100, 20, key="lb_wk")
        top = helper.top_bowlers(data, min_wk).head(15)
        fig = px.bar(
            top.reset_index(),
            x="wickets",
            y="Player_Name",
            orientation="h",
            title=f"Top Wicket Takers (min {min_wk} wickets)",
            labels={"wickets": "Wickets", "Player_Name": ""},
            color="wickets",
            color_continuous_scale="Blues",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            top[["wickets", "economy", "bowling_avg", "five_wickets"]],
            use_container_width=True,
        )

    with tab_all:
        st.caption("Balanced score from normalized runs and wickets.")
        ar = helper.all_rounders(data).head(15)
        if ar.empty:
            st.info("No players meet the default thresholds (500 runs & 30 wickets).")
        else:
            fig = px.scatter(
                ar.reset_index(),
                x="runs",
                y="wickets",
                text="Player_Name",
                size="score",
                title="All-Rounder Map (size = combined score)",
                labels={"runs": "Career Runs", "wickets": "Career Wickets"},
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(height=480)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(ar, use_container_width=True)

    with tab_power:
        ph = helper.power_hitters(data).head(15)
        fig = px.bar(
            ph.reset_index().head(10),
            x="Player_Name",
            y="sixes",
            title="Most Sixes (min 200 career runs)",
            color="strike_rate",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(ph, use_container_width=True)

    with tab_mile:
        mp = helper.milestone_players(data)
        st.dataframe(mp, use_container_width=True)

# ── Player Analysis ───────────────────────────────────────────────────────────
elif user_menu == "Player Analysis":
    st.title("Player Analysis")
    players = [""] + sorted(data["Player_Name"].unique().tolist())
    player = st.selectbox("Select player", players, index=0)

    if not player:
        st.info("Choose a player to view their career profile.")
    else:
        summary = helper.player_career_summary(data, player)
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Seasons", summary["seasons"])
        m2.metric("Runs", f"{summary['runs']:,}")
        m3.metric("Wickets", summary["wickets"])
        m4.metric("Avg", summary["average"])
        m5.metric("SR", summary["strike_rate"])
        m6.metric("Economy", summary["economy"] if summary["wickets"] else "—")

        m7, m8, m9, m10 = st.columns(4)
        m7.metric("100s", summary["centuries"])
        m8.metric("50s", summary["half_centuries"])
        m9.metric("Highest", summary["highest"])
        m10.metric("5W Hauls", summary["five_wickets"])

        history = helper.player_season_history(data, player)
        col_l, col_r = st.columns(2)

        with col_l:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=history["Year"], y=history["Runs_Scored"], name="Runs")
            )
            fig.update_layout(title="Runs by Season", height=320, margin=dict(t=40))
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            if history["Wickets_Taken"].sum() > 0:
                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=history["Year"],
                        y=history["Wickets_Taken"],
                        name="Wickets",
                        marker_color="#004E89",
                    )
                )
                fig.update_layout(
                    title="Wickets by Season", height=320, margin=dict(t=40)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No bowling data for this player.")

        if history["Sixes"].sum() > 0:
            fig = px.line(
                history,
                x="Year",
                y="Sixes",
                markers=True,
                title="Sixes per Season",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Season-by-Season Stats")
        st.dataframe(history, use_container_width=True, hide_index=True)

        csv = history.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download player stats (CSV)",
            csv,
            file_name=f"{player.replace(' ', '_')}_ipl_stats.csv",
            mime="text/csv",
        )

# ── Season Analysis ───────────────────────────────────────────────────────────
elif user_menu == "Season Analysis":
    st.title("Season Analysis")
    year = st.selectbox("Select season", years, index=len(years) - 1)
    summary = helper.season_summary(data, year)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Active Players", summary["players"])
    s2.metric("Total Runs", f"{summary['total_runs']:,}")
    s3.metric("Total Wickets", summary["total_wickets"])
    s4.metric("Orange Cap", summary["top_scorer"])
    s5.metric("Purple Cap", summary["top_wicket_taker"])

    s6, s7, s8 = st.columns(3)
    s6.metric("Sixes", summary["total_sixes"])
    s7.metric("Fours", summary["total_fours"])
    s8.metric("Centuries", summary["centuries"])

    season_df = data[data["Year"] == year].copy()

    col1, col2 = st.columns(2)
    with col1:
        bat = (
            season_df[season_df["Runs_Scored"] > 0]
            .groupby("Player_Name")["Runs_Scored"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig = px.bar(
            bat.reset_index(),
            x="Runs_Scored",
            y="Player_Name",
            orientation="h",
            title=f"Top Run Scorers — IPL {year}",
            color_discrete_sequence=["#FF6B35"],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        bowl = (
            season_df[season_df["Wickets_Taken"] > 0]
            .groupby("Player_Name")["Wickets_Taken"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        if not bowl.empty:
            fig = px.bar(
                bowl.reset_index(),
                x="Wickets_Taken",
                y="Player_Name",
                orientation="h",
                title=f"Top Wicket Takers — IPL {year}",
                color_discrete_sequence=["#004E89"],
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Full {year} Player Stats")
    display_cols = [
        "Player_Name",
        "Runs_Scored",
        "Batting_Average",
        "Batting_Strike_Rate",
        "Wickets_Taken",
        "Economy_Rate",
        "Sixes",
        "Centuries",
    ]
    st.dataframe(
        season_df[display_cols].sort_values("Runs_Scored", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

# ── Compare Players ───────────────────────────────────────────────────────────
elif user_menu == "Compare Players":
    st.title("Compare Players")
    player_list = sorted(data["Player_Name"].unique().tolist())
    c1, c2 = st.columns(2)
    p1 = c1.selectbox("Player 1", player_list, index=0)
    p2 = c2.selectbox(
        "Player 2",
        player_list,
        index=min(1, len(player_list) - 1),
    )

    if p1 == p2:
        st.warning("Select two different players.")
    else:
        s1 = helper.player_career_summary(data, p1)
        s2 = helper.player_career_summary(data, p2)
        metrics = [
            ("Runs", "runs"),
            ("Wickets", "wickets"),
            ("Average", "average"),
            ("Strike Rate", "strike_rate"),
            ("Centuries", "centuries"),
            ("Sixes", "sixes"),
        ]

        rows = []
        for label, key in metrics:
            rows.append(
                {
                    "Metric": label,
                    p1: s1[key],
                    p2: s2[key],
                }
            )
        compare_df = pd.DataFrame(rows)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)

        h1 = helper.player_season_history(data, p1)
        h2 = helper.player_season_history(data, p2)
        merged = h1[["Year", "Runs_Scored"]].merge(
            h2[["Year", "Runs_Scored"]],
            on="Year",
            how="outer",
            suffixes=(f" ({p1})", f" ({p2})"),
        ).fillna(0)

        fig = px.line(
            merged,
            x="Year",
            y=[c for c in merged.columns if c != "Year"],
            markers=True,
            title="Runs by Season — Head to Head",
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
elif user_menu == "Insights":
    st.title("League Insights")

    col1, col2 = st.columns(2)
    with col1:
        six_df = (
            data.groupby("Year")["Sixes"]
            .sum()
            .reset_index()
            .rename(columns={"Sixes": "Total_Sixes"})
        )
        fig = px.area(
            six_df,
            x="Year",
            y="Total_Sixes",
            title="Six-Hitting Trend by Season",
            color_discrete_sequence=["#E63946"],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cen_df = (
            data.groupby("Year")["Centuries"]
            .sum()
            .reset_index()
            .rename(columns={"Centuries": "Total_Centuries"})
        )
        fig = px.line(
            cen_df,
            x="Year",
            y="Total_Centuries",
            markers=True,
            title="Centuries per Season",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Batting vs Bowling Activity")
    activity = data.groupby("Year").agg(
        batters=("Runs_Scored", lambda x: (x > 0).sum()),
        bowlers=("Wickets_Taken", lambda x: (x > 0).sum()),
    ).reset_index()
    fig = px.bar(
        activity,
        x="Year",
        y=["batters", "bowlers"],
        barmode="group",
        title="Contributing Batters & Bowlers per Season",
        labels={"value": "Count", "variable": "Role"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Economy Leaders (min 500 balls, career)")
    bowl = helper.career_bowling_stats(data)
    eco = bowl[bowl["balls_bowled"] >= 500].sort_values("economy").head(10)
    st.dataframe(eco[["wickets", "economy", "bowling_avg", "matches_bowled"]], use_container_width=True)

st.sidebar.divider()
st.sidebar.markdown(
    "**Data:** `cricket_data_2025.csv`  \n"
    "Run locally: `streamlit run main.py`"
)
