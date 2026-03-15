"""
F1 Race Summary Dashboard
=========================
A comprehensive visualization of a race weekend including:
1. Tyre Strategy
2. Team Pace Ranking
3. Top 10 Position Changes
4. Track Map with Speed Heatmap
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
import fastf1
import fastf1.plotting

# Setup plotting
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')

def create_race_summary(year, location, session_type='R'):
    # Load session
    print(f"Loading {year} {location} {session_type}...")
    session = fastf1.get_session(year, location, session_type)
    session.load()
    laps = session.laps

    # Create figure with GridSpec
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1, 1.2], width_ratios=[1, 1])
    
    fig.suptitle(f"{year} {session.event['EventName']} - Race Summary", size=24, y=0.95)

    # --- 1. Tyre Strategy (Top Left) ---
    ax_strat = fig.add_subplot(gs[0, 0])
    drivers = session.drivers
    drivers = [session.get_driver(d)["Abbreviation"] for d in drivers]
    
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})

    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]
        prev_end = 0
        for _, row in driver_stints.iterrows():
            ax_strat.barh(y=driver, width=row["StintLength"], left=prev_end,
                         color=fastf1.plotting.get_compound_color(row["Compound"], session=session),
                         edgecolor="black")
            prev_end += row["StintLength"]
    
    ax_strat.set_title("Tyre Strategy", fontsize=15)
    ax_strat.invert_yaxis()
    ax_strat.set_xlabel("Lap Number")

    # --- 2. Team Pace Ranking (Top Right) ---
    ax_pace = fig.add_subplot(gs[0, 1])
    quick_laps = laps.pick_quicklaps().copy()
    quick_laps["LapTime(s)"] = quick_laps["LapTime"].dt.total_seconds()
    
    team_order = quick_laps.groupby("Team")["LapTime(s)"].median().sort_values().index
    team_palette = {team: fastf1.plotting.get_team_color(team, session=session) for team in team_order}
    
    sns.boxplot(data=quick_laps, x="Team", y="LapTime(s)", order=team_order, palette=team_palette, ax=ax_pace, whiskerprops=dict(color="white"))
    ax_pace.set_title("Team Pace Ranking (Median)", fontsize=15)
    ax_pace.set_xticklabels(team_order, rotation=45)
    ax_pace.set_xlabel("")

    # --- 3. Position Changes Top 10 (Bottom Left) ---
    ax_pos = fig.add_subplot(gs[1, 0])
    top_10 = session.results.iloc[:10]['Abbreviation'].tolist()
    
    for abb in top_10:
        drv_laps = laps.pick_drivers(abb)
        style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=session)
        ax_pos.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)
    
    ax_pos.set_ylim([20.5, 0.5])
    ax_pos.set_yticks(range(1, 21))
    ax_pos.set_title("Position Changes (Top 10)", fontsize=15)
    ax_pos.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    ax_pos.set_xlabel("Lap")
    ax_pos.set_ylabel("Position")

    # --- 4. Track Map Speed Heatmap (Bottom Right) ---
    ax_map = fig.add_subplot(gs[1, 1])
    fastest_lap = laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry().add_distance()
    
    x = telemetry['X']
    y = telemetry['Y']
    color = telemetry['Speed']

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap='plasma', norm=norm, linestyle='-', linewidth=5)
    lc.set_array(color)
    
    ax_map.add_collection(lc)
    ax_map.axis('equal')
    ax_map.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)
    ax_map.set_title(f"Fastest Lap Speed Heatmap ({fastest_lap['Driver']})", fontsize=15)
    
    cbar = fig.colorbar(lc, ax=ax_map, fraction=0.046, pad=0.04)
    cbar.set_label('Speed (km/h)')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    # Get user input for the race
    try:
        print("--- F1 Race Summary Tool ---")
        year_input = input("Enter Year (e.g., 2024): ")
        year = int(year_input)
        location = input("Enter Track Location (e.g., Qatar, Vegas, Monza): ")
        
        create_race_summary(year, location)
    except ValueError:
        print("Error: Year must be a number.")
    except Exception as e:
        print(f"An error occurred: {e}")
