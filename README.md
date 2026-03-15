# F1 Race Analysis & Visualization

A comprehensive collection of Python tools for Formula 1 data analysis using the `FastF1` library. This repository provides everything from high-level race overviews to deep-dive driver telemetry comparisons.

## 🚀 Key Features

### 1. Interactive Dashboards
*   **`race_summary.py`**: A complete weekend overview including tyre strategy, team pace rankings, position changes for the top 10, and a track map speed heatmap.
*   **`driver_summary.py`**: A deep dive into an individual driver's performance. Shows race/season points, detailed stint strategy, and aligned Speed vs. Brake telemetry for their fastest lap.
*   **`driver_compare.py`**: Side-by-side comparison of two drivers. Overlays their telemetry (Speed & Brake) and stacks their strategies to show where performance gaps exist.

### 2. Specialized Analytical Plots
*   **Track Analysis**: `plot_annotate_corners.py` (Map with corner numbers), `plot_speed_traces.py` (Speed vs Distance comparison).
*   **Pace & Strategy**: `plot_team_pace_ranking.py` (Boxplots), `plot_strategy.py` (Full grid pit-stop timeline), `plot_laptimes_distribution.py` (Violin/Swarm plots).
*   **Race Dynamics**: `plot_position_changes.py` (Lap-by-lap tracking), `plot_driver_laptimes.py` (Scatter plots by compound).

---

## 🛠️ Installation

### Prerequisites
*   Python 3.8 or higher.
*   A stable internet connection (for downloading race data).

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/eshanganju/F1Analyses.git
   cd F1Analyses
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv F1
   source F1/bin/activate  # On Windows: F1\Scripts\activate
   pip install -r requirements.txt
   ```

---

## 📊 Usage

The main dashboard scripts are interactive and will prompt you for the **Year**, **Track Location**, and **Driver Abbreviations**.

### Run a Race Summary
```bash
python race_summary.py
# Prompts: 2024, Qatar
```

### Run a Driver Performance Review
```bash
python driver_summary.py
# Prompts: 2024, Qatar, NOR
```

### Compare Two Drivers
```bash
python driver_compare.py
# Prompts: 2024, Qatar, VER, HAM
```

> **Note on Driver Abbreviations:** Use standard 3-letter codes (e.g., VER, HAM, NOR, LEC, PIA).
> **Note on Locations:** Use common names like `Vegas`, `Monza`, `Silverstone`, or `Spa`.

---

## 📦 Dependencies
*   `fastf1`: Core library for F1 data access.
*   `matplotlib` & `seaborn`: Visualization and plotting.
*   `numpy` & `pandas`: Data manipulation.

## 📄 License
This project is for educational and analytical purposes. Data is provided by the FastF1 library.
