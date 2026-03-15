"""
Driver Comparison Tool
======================
Compares two drivers' performance in a race:
1. Side-by-side Race Stats (Race & Season Points)
2. Speed & Brake Trace Comparison (Separate aligned plots)
3. Stacked Tyre Strategies
"""

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import fastf1
import fastf1.plotting

# Setup plotting
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')

def create_driver_comparison(year, location, dri1_abb, dri2_abb):
    print(f"Loading {year} {location} for comparison: {dri1_abb} vs {dri2_abb}...")
    session = fastf1.get_session(year, location, 'R')
    session.load()
    
    # Data for Driver 1
    d1_res = session.results.loc[session.results['Abbreviation'] == dri1_abb].iloc[0]
    d1_laps = session.laps.pick_drivers(dri1_abb)
    d1_fastest = d1_laps.pick_fastest()
    d1_tel = d1_fastest.get_telemetry().add_distance()
    d1_color = fastf1.plotting.get_team_color(d1_res['TeamName'], session=session)

    # Data for Driver 2
    d2_res = session.results.loc[session.results['Abbreviation'] == dri2_abb].iloc[0]
    d2_laps = session.laps.pick_drivers(dri2_abb)
    d2_fastest = d2_laps.pick_fastest()
    d2_tel = d2_fastest.get_telemetry().add_distance()
    d2_color = fastf1.plotting.get_team_color(d2_res['TeamName'], session=session)

    # If colors are the same (teammates), make one slightly different
    if d1_color == d2_color:
        d2_color = 'white'

    # Create Figure
    fig = plt.figure(figsize=(16, 14))
    gs = GridSpec(5, 2, figure=fig, height_ratios=[1, 2, 2, 1, 0.1]) # Adding row for strategy
    
    fig.suptitle(f"Comparison: {dri1_abb} vs {dri2_abb}\n{year} {session.event['EventName']}", size=20)

    # Function to get points
    def get_points(res):
        race = res['Points']
        season = "N/A"
        for col in res.index:
            if "Total" in col or "Season" in col:
                season = res[col]
                break
        return race, season

    # --- 1. Summary Cards (Top Row) ---
    for i, (abb, res, fastest, color) in enumerate([(dri1_abb, d1_res, d1_fastest, d1_color), 
                                                    (dri2_abb, d2_res, d2_fastest, d2_color)]):
        ax = fig.add_subplot(gs[0, i])
        ax.axis('off')
        race_pts, season_pts = get_points(res)
        
        summary_text = (
            f"DRIVER: {res['FullName']}\n"
            f"Team: {res['TeamName']}\n"
            f"---------------------------\n"
            f"Finish: P{int(res['ClassifiedPosition'])} (Grid: P{int(res['GridPosition'])})\n"
            f"Race Points: {race_pts} | Season Total: {season_pts}\n"
            f"Fastest Lap: {fastest['LapTime'].total_seconds():.3f}s (Lap {int(fastest['LapNumber'])})\n"
            f"Tyre: {fastest['Compound']}"
        )
        ax.text(0.5, 0.5, summary_text, fontsize=12, va='center', ha='center', 
                bbox=dict(boxstyle='round,pad=1', facecolor='black', alpha=0.5, edgecolor=color))

    # --- 2. Telemetry: Speed (Second Row) ---
    ax_speed = fig.add_subplot(gs[1, :])
    ax_speed.plot(d1_tel['Distance'], d1_tel['Speed'], color=d1_color, label=f"{dri1_abb} Speed", linewidth=2)
    ax_speed.plot(d2_tel['Distance'], d2_tel['Speed'], color=d2_color, label=f"{dri2_abb} Speed", linewidth=2, linestyle='--')
    ax_speed.set_title("Fastest Lap Telemetry: Speed Comparison", fontsize=15)
    ax_speed.set_ylabel("Speed (km/h)")
    ax_speed.legend(loc='upper right')
    plt.setp(ax_speed.get_xticklabels(), visible=False)

    # --- 3. Telemetry: Brake (Third Row - Aligned with Speed) ---
    ax_brake = fig.add_subplot(gs[2, :], sharex=ax_speed)
    ax_brake.plot(d1_tel['Distance'], d1_tel['Brake'], color=d1_color, label=f"{dri1_abb} Brake %", linewidth=2)
    ax_brake.plot(d2_tel['Distance'], d2_tel['Brake'], color=d2_color, label=f"{dri2_abb} Brake %", linewidth=2, linestyle='--')
    ax_brake.set_title("Fastest Lap Telemetry: Brake Input Comparison", fontsize=15)
    ax_brake.set_xlabel("Distance (m)")
    ax_brake.set_ylabel("Brake (%)")
    ax_brake.legend(loc='upper right')

    # --- 4. Stacked Tyre Strategy (Fourth Row) ---
    ax_strat = fig.add_subplot(gs[3, :])
    for i, (abb, laps) in enumerate([(dri1_abb, d1_laps), (dri2_abb, d2_laps)]):
        stints = laps[["Stint", "Compound", "LapNumber"]].groupby(["Stint", "Compound"]).count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})
        prev_end = 0
        for _, row in stints.iterrows():
            comp_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
            ax_strat.barh(y=abb, width=row["StintLength"], left=prev_end, color=comp_color, edgecolor='black')
            ax_strat.text(prev_end + row["StintLength"]/2, i, str(row["StintLength"]), 
                         va='center', ha='center', color='black', fontweight='bold')
            prev_end += row["StintLength"]
    ax_strat.set_title("Strategy Comparison (Laps per Stint)", fontsize=15)
    ax_strat.set_xlabel("Lap Number")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    try:
        print("--- F1 Driver Comparison Tool ---")
        year = int(input("Enter Year (e.g., 2024): "))
        location = input("Enter Track Location (e.g., Qatar, Vegas): ")
        driver1 = input("Enter Driver 1 Abbreviation (e.g., VER): ").upper()
        driver2 = input("Enter Driver 2 Abbreviation (e.g., HAM): ").upper()
        
        create_driver_comparison(year, location, driver1, driver2)
    except Exception as e:
        print(f"Error: {e}")
