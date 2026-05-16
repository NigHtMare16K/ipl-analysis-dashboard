# IPL Analysis Web App

An interactive **Streamlit** dashboard for exploring Indian Premier League (IPL) player statistics from **2008 to 2024**. The app loads season-wise player records, aggregates career metrics, and visualizes trends with Plotly charts.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)

## Features

| Section | Description |
|--------|-------------|
| **Home** | Overview metrics, runs/wickets per season charts, dataset preview |
| **Leaderboard** | Top run scorers, wicket takers, all-rounders, power hitters, century makers |
| **Player Analysis** | Career summary, season trends, CSV export |
| **Season Analysis** | Year-wise totals, Orange/Purple cap leaders, full season table |
| **Compare Players** | Side-by-side career stats and runs-over-time comparison |
| **Insights** | Six-hitting trends, centuries, economy leaders, batting vs bowling activity |

### Highlights

- Career stats computed correctly (e.g. strike rate from total runs/balls, not averaged season SRs)
- Qualification filters on leaderboards (minimum innings/wickets)
- All-rounder scatter plot with combined performance score
- Cached data loading for faster reloads
- Portable dataset path (no hard-coded drive letters)

## Dataset

Place `cricket_data_2025.csv` in the project root. Each row is a **player-season** record with batting and bowling columns, including:

`Year`, `Player_Name`, `Runs_Scored`, `Wickets_Taken`, `Batting_Average`, `Batting_Strike_Rate`, `Economy_Rate`, `Sixes`, `Centuries`, and more.

Rows with missing `Year` or `"No stats"` values are cleaned during preprocessing.

## Project Structure

```
IPL-Analysis-Web-App/
├── main.py              # Streamlit UI
├── helper.py            # Analytics & aggregations
├── preprocessor.py      # Data loading & cleaning
├── cricket_data_2025.csv
├── requirements.txt
└── README.md
```

## Setup & Run

1. **Clone or download** this repository.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the app**:

   ```bash
   streamlit run main.py
   ```

5. Open the URL shown in the terminal (usually `http://localhost:8501`).

## Requirements

- Python 3.9+
- See `requirements.txt` for package versions

## Screenshots

After launching, use the sidebar to switch between Home, Leaderboard, Player Analysis, Season Analysis, Compare Players, and Insights.

## Future Ideas

- Team/franchise column for franchise-level analysis
- Match-by-match ball data integration
- User-defined filters saved as bookmarks

## License

Educational / portfolio use. Dataset attribution belongs to its original source.
