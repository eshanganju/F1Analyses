"""
Driver Performance Summary
==========================
Analyzes a specific driver's performance in a race:
1. Fastest Lap Time & Race Info
2. Race Points & Season Points
3. Speed & Brake Trace (Separate aligned plots)
4. Tyre Strategy
"""

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import fastf1
import fastf1.plotting

# Setup plotting
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')

def create_driver_summary(year, location, driver_abb):
    print(f"Loading {year} {location} for driver {driver_abb}...")
    session = fastf1.get_session(year, location, 'R')
    session.load()
    
    # Get driver data
    driver_results = session.results.loc[session.results['Abbreviation'] == driver_abb].iloc[0]
    driver_laps = session.laps.pick_drivers(driver_abb)
    fastest_lap = driver_laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry().add_distance()
    
    # Season points usually aren't directly in the race result, 
    # but we can try to look for it in the results or mention it's unavailable if not there.
    # We'll use 'Points' for race points.
    race_points = driver_results['Points']
    
    # Attempt to find Season Points (depends on fastf1 version and data availability)
    # We'll check if any other column seems to represent total season points.
    season_points = "N/A"
    for col in session.results.columns:
        if "Total" in col or "Season" in col:
            season_points = driver_results[col]
            break

    # Create Figure
    fig = plt.figure(figsize=(15, 12))
    # Using more rows to separate Speed and Brake
    gs = GridSpec(4, 2, figure=fig, height_ratios=[1, 1.5, 1.5, 1])
    
    fig.suptitle(f"{driver_abb} - {year} {session.event['EventName']} Summary", size=20)

    # --- 1. Text Summary (Top Left) ---
    ax_info = fig.add_subplot(gs[0, 0])
    ax_info.axis('off')
    
    info_text = (
        f"Driver: {driver_results['FullName']}\n"
        f"Team: {driver_results['TeamName']}\n"
        f"Grid Position: {int(driver_results['GridPosition'])}\n"
        f"Finish Position: {int(driver_results['ClassifiedPosition'])}\n"
        f"Status: {driver_results['Status']}"
    )
    ax_info.text(0, 0.5, info_text, fontsize=14, verticalalignment='center')

    # --- 2. Points & Fastest Lap (Top Right) ---
    ax_stats = fig.add_subplot(gs[0, 1])
    ax_stats.axis('off')
    
    stats_text = (
        f"Race Points: {race_points}\n"
        f"Season Points: {season_points}\n"
        f"Fastest Lap: {fastest_lap['LapTime'].total_seconds():.3f}s\n"
        f"Lap Number: {int(fastest_lap['LapNumber'])}\n"
        f"Compound: {fastest_lap['Compound']}"
    )
    ax_stats.text(0, 0.5, stats_text, fontsize=14, verticalalignment='center', fontweight='bold')

    # --- 3. Telemetry: Speed (Second Row) ---
    ax_speed = fig.add_subplot(gs[1, :])
    team_color = fastf1.plotting.get_team_color(driver_results['TeamName'], session=session)
    
    ax_speed.plot(telemetry['Distance'], telemetry['Speed'], color='white', linewidth=2, label='Speed')
    ax_speed.set_ylabel('Speed (km/h)')
    ax_speed.set_title(f"Fastest Lap Telemetry ({fastest_lap['Compound']} Tires) - Lap {int(fastest_lap['LapNumber'])}")
    ax_speed.legend(loc='upper right')
    # Remove x-ticks from speed as it shares x-axis with brake
    plt.setp(ax_speed.get_xticklabels(), visible=False)

    # --- 4. Telemetry: Brake (Third Row - Aligned with Speed) ---
    ax_brake = fig.add_subplot(gs[2, :], sharex=ax_speed)
    ax_brake.plot(telemetry['Distance'], telemetry['Brake'], color=team_color, linewidth=2, label='Brake %')
    ax_brake.set_xlabel('Distance (m)')
    ax_brake.set_ylabel('Brake (%)')
    ax_brake.legend(loc='upper right')

    # --- 5. Tyre Strategy (Bottom Row) ---
    ax_strat = fig.add_subplot(gs[3, :])
    stints = driver_laps[["Stint", "Compound", "LapNumber"]].groupby(["Stint", "Compound"]).count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})

    prev_end = 0
    for _, row in stints.iterrows():
        color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
        ax_strat.barh(y=driver_abb, width=row["StintLength"], left=prev_end, color=color, edgecolor="black")
        ax_strat.text(prev_end + row["StintLength"]/2, driver_abb, str(row["StintLength"]), 
                     va='center', ha='center', color='black', fontweight='bold')
        prev_end += row["StintLength"]

    ax_strat.set_title("Tyre Strategy (Laps per Stint)")
    ax_strat.set_xlabel("Lap Number")
    ax_strat.set_yticks([])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    try:
        print("--- F1 Driver Summary Tool ---")
        year = int(input("Enter Year (e.g., 2024): "))
        location = input("Enter Track Location (e.g., Qatar, Vegas): ")
        driver = input("Enter Driver Abbreviation (e.g., HAM, VER, NOR): ").upper()
        
        create_driver_summary(year, location, driver)
    except Exception as e:
        print(f"Error: {e}")
