Personal Finance Analyzer

Quick start

- Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- Run the CLI on the sample data:

```bash
python -m src.main --file data/transactions.csv
```

- Run tests:

```bash
python -m pytest -q
```

# Personal Finance Analyzer

A small Python project that analyzes transaction CSVs and provides both a CLI and an interactive Streamlit dashboard for exploring your personal finances.

Features
- Load transactions from CSV and normalize dates
- Produce monthly metrics and category breakdowns
- Visualizations: monthly income vs expenses, category spending, savings trend
- Streamlit dashboard for interactive exploration and CSV upload

Requirements
- Python 3.10+ recommended
- See `requirements.txt` for exact dependencies (includes `pandas`, `matplotlib`, `seaborn`, `streamlit`).

Quick setup
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the Streamlit dashboard (recommended)

From the project root (important), run:

```powershell
cd "c:\Users\jasae\Python Projects\Personal Finance Analyzer"
streamlit run src/dashboard.py
```

Then open http://localhost:8501 (or the port Streamlit reports) in your browser. Use the left sidebar to upload a CSV or use the included sample `data/transactions.csv`, normalize dates, and switch visualizations.

Notes about imports and troubleshooting
- If you see "ModuleNotFoundError: No module named 'src'", make sure you run Streamlit from the project root directory (the repository root that contains `src/` and `requirements.txt`).
- The dashboard also inserts the project root on `sys.path` at runtime to help Streamlit find the `src` package when launched from the repo root.

CLI usage

You can run a simple CLI summary instead of the dashboard:

```powershell
python -m src.main --file data/transactions.csv
```

This prints a transactions summary, and optionally can load data into a sqlite DB or produce plots (see `--help`).

Tests

Run the test suite with:

```powershell
python -m pytest -q
```

Files of interest
- `src/dashboard.py` — Streamlit app
- `src/main.py` — CLI entrypoint
- `src/transactions.py`, `src/reports.py`, `src/viz.py` — core logic and plotting
- `data/transactions.csv` — sample data used by the dashboard

Deploying to Streamlit Cloud

1. Push this repo (including `README.md` and `requirements.txt`) to GitHub.
2. On https://share.streamlit.io create a new app and point it at `src/dashboard.py`.


