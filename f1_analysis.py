import fastf1
import fastf1.plotting
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import numpy as np
import gui
import seaborn as sns
from collections import defaultdict
from scipy.interpolate import interp1d
import streamlit as st

# Define team colors
TEAM_COLORS = {
    "Mercedes": "#6CD3BF",
    "Red Bull Racing": "#1E41FF",
    "Ferrari": "#DC0000",
    "McLaren": "#FF8700",
    "Aston Martin": "#358C75",
    "Alpine": "#2293D1",
    "Williams": "#37BEDD",
    "Haas F1 Team": "#B6BABD",
    "Kick Sauber": "#52E252",
    "RB": "#5E8FAA",
    "Racing Bulls": "#FFFFFF",
    "Renault": "#FFF500",
    "Racing Point": "#F596C8",
    "Toro Rosso": "#469BFF",
    "Force India": "#FF80C7",
    "BMW Sauber": "#FFFFFF",
    "Lotus": "#FFB800",
    "Toyota": "#E4002B",
    "Alfa Romeo Racing": "#900000",
    "Alfa Romeo": "#900000",
    "AlphaTauri": "#2B4562"
}


# Load F1 session data dynamically from GUI selections
def load_session(mode, year, grand_prix, session_type):
    if mode == "Grand Prix":
        session_mapping = {
            "FP1": "FP1",
            "FP2": "FP2",
            "FP3": "FP3",
            "Sprint Qualifying": "Sprint Qualifying",
            "Qualifying": "Qualifying",
            "Sprint Race": "Sprint",
            "Race": "Race"
        }

        if not all([year, grand_prix, session_type]):
            return None

        try:
            #Check if the Grand Prix exists in that year
            event = fastf1.get_event(int(year), grand_prix)

            if event.Country is None:
                st.warning(f"{grand_prix} **did not host** a race weekend in {year}.")
                return None

            # Check if session was held in that weekend
            session = fastf1.get_session(int(year), grand_prix, session_mapping[session_type])
            session.load()

            return session

        except Exception as e:
            st.warning(f"Error loading session: {e}")
            return None

    return None

'''------------------------------------------------------------------------------------'''

'''RACE PLOTS'''

# Plot 1: Stint comparison between drivers
def plot_stint_comparison(session, drivers, team_colors):

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(16, 9), dpi=1000)
    
    driver_positions = {}
    pit_lap_counts = defaultdict(int)  # Track how many pit stops happened on each lap
    
    for driver in drivers:
        laps = session.laps.pick_drivers(driver)

        team = laps.iloc[0]["Team"]  
        color = team_colors.get(team, "white")  
        final_position = laps.iloc[-1]["Position"]  
        pit_stops = laps["PitInTime"].count()
        driver_positions[driver] = final_position

        # Get lap numbers and valid lap times
        valid_laps = laps.dropna(subset=["LapTime"])
        valid_laps = valid_laps[~valid_laps["PitInTime"].notna()]  # Remove inlaps
        valid_laps = valid_laps[~valid_laps["PitOutTime"].notna()]  # Remove outlaps

        lap_numbers = valid_laps["LapNumber"].values
        lap_times = valid_laps["LapTime"].dt.total_seconds().values
        
        # Filter out unrealistic lap times (e.g., greater than 200s)
        lap_times = np.where((lap_times > 200), np.nan, lap_times)

        # Identify pit exit laps
        pit_exit_laps = laps[laps["PitOutTime"].notna()]["LapNumber"].values

        # Remove first recorded lap if it's a pit exit (start from the pit lane)
        if pit_exit_laps.size > 0 and pit_exit_laps[0] == 1:
            pit_exit_laps = pit_exit_laps[1:]  

        # Plot stint comparison
        ax.plot(lap_numbers, lap_times, color=color, linewidth=2, label=f"{driver} P{int(final_position)}, {pit_stops} stop")

        # Mark pit exit laps with vertical dashed lines
        offset = 0.15  # offset to separate overlapping lines
        for pit_exit in pit_exit_laps:
            pit_lap_counts[pit_exit] += 1  # Count pit stops on this lap
            shift = (pit_lap_counts[pit_exit] - 1) * offset  # Adjust position
            
            ax.axvline(x=pit_exit + shift, color=color, linestyle="-.", alpha=0.8, linewidth=1)

    # Warning
    if pit_stops > 3:
        st.warning('A Safety Car through the pit lane could be present, be careful about pit stop count.')

    # Plotting
    driver_info = " vs ".join([f"{driver} (P{int(pos)})" for driver, pos in driver_positions.items()])
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time (s)")
    ax.set_title(f"{session.event['EventName']} {session.event.year} {session.name}\n"
                 "Stint Comparison \n"
                 f"{driver_info}", fontsize=14)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    return fig

# Plot 2: Lap time distribution
def plot_lap_time_distribution(session, team_colors):
    plt.style.use("dark_background")
    
    laps = session.laps.pick_quicklaps()
    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )
    print(team_order)

    team_palette = {team: team_colors.get(team, "#888888") for team in team_order}

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 9), dpi=1000)
    
    # Plotting
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        hue="Team",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
        ax=ax  # Check if plot is drawn on the correct axis
    )

    ax.set_title(f"{session.event['EventName']} {session.event.year} {session.name}\n"
                 f"Lap Time Distribution", fontsize=14)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set(xlabel=None)
    plt.tight_layout()
    
    return fig 


'''--------------------------------------------------------------------'''

'''QUALIFYING PLOTS'''

# Plot 1: Best Lap per Team in Qualifying
def plot_best_laps(session):
    plt.style.use("dark_background") 

    # Pick fastest laps by team
    fastest_laps = session.laps.loc[session.laps.groupby("Team")["LapTime"].idxmin()]
    fastest_laps = fastest_laps.sort_values("LapTime")

    teams = fastest_laps["Team"]
    delta_time = (fastest_laps["LapTime"] - fastest_laps["LapTime"].min()).dt.total_seconds()
    
    # Get best lap time and driver
    best_lap_time = fastest_laps["LapTime"].min()
    best_driver = fastest_laps.loc[fastest_laps["LapTime"].idxmin(), "Driver"]

    # Format time to m:ss.sss
    total_seconds = best_lap_time.total_seconds()
    formatted_time = f"{int(total_seconds // 60)}:{total_seconds % 60:06.3f}"  

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 9), dpi=1000)

    # Use team colors
    colors = [TEAM_COLORS.get(team, "gray") for team in teams]

    # Plotting
    ax.barh(teams, delta_time, color=colors)
    ax.set_xlabel("Delta Time (s)")
    ax.set_ylabel("Team")
    ax.invert_yaxis()
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle(
        f"Best Lap Time Per Team\n"
        f"{session.event['EventName']} {session.event.year} {session.name}\n"
        f"Fastest Lap: {best_driver} {formatted_time}\n",
        fontsize=14
    )

    plt.tight_layout()

    return fig

# Plot 2: Lap Time Comparison
def plot_lap_comparison(session, driver1, driver2):
    plt.style.use("dark_background")

    # Get fastest lap telemetry for both drivers
    lapdata1 = session.laps.pick_drivers(driver1).pick_fastest()
    lapdata2 = session.laps.pick_drivers(driver2).pick_fastest()

    # Be sure drivers participated to the session
    if lapdata1 is None:
        st.warning(f"No laps completed for **{driver1}**, probably crash or substituted by a rookie. Cannot display lap comparison with {driver2}.")
        return None
    if lapdata2 is None:
        st.warning(f"No laps completed for **{driver2}**, probably crash or substituted by a rookie. Cannot display lap comparison with {driver1}.")
        return None
    else:
        lap1 = lapdata1.get_telemetry().add_distance()
        lap2 = lapdata2.get_telemetry().add_distance()

        driver1_team = lapdata1["Team"]
        driver2_team = lapdata2["Team"]
        
        color1 = TEAM_COLORS.get(driver1_team, "gray")
        color2 = TEAM_COLORS.get(driver2_team, "gray")

        # Format laptimes individually
        def format_time(timedelta):
            total_seconds = timedelta.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            millis = int((total_seconds - minutes * 60 - seconds) * 1000)
            return f"{minutes}:{seconds:02}.{millis:03}"

        lap_time1 = lapdata1["LapTime"]
        lap_time2 = lapdata2["LapTime"]

        formatted_time1 = format_time(lap_time1)
        formatted_time2 = format_time(lap_time2)

        # Create figure and axes
        fig, axs = plt.subplots(3, 1, figsize=(16, 9), dpi=1000)

        # Speed comparison
        axs[0].plot(lap1["Distance"], lap1["Speed"], label=driver1, color=color1)
        axs[0].plot(lap2["Distance"], lap2["Speed"], label=driver2, color=color2)
        axs[0].set_ylabel("Speed (km/h)")
        axs[0].legend()
        axs[0].grid(True, linestyle="--", alpha=0.5)

        # Throttle comparison
        axs[1].plot(lap1["Distance"], lap1["Throttle"], label=driver1, color=color1)
        axs[1].plot(lap2["Distance"], lap2["Throttle"], label=driver2, color=color2)
        axs[1].set_ylabel("Throttle (%)")
        axs[1].grid(True, linestyle="--", alpha=0.5)

        # Convert Timedelta to total seconds
        lap1_time_seconds = lap1["Time"].dt.total_seconds()
        lap2_time_seconds = lap2["Time"].dt.total_seconds()

        lap1_time_seconds -= lap1_time_seconds.iloc[0]
        lap2_time_seconds -= lap2_time_seconds.iloc[0]

        # Convert distances into percentage of lap completion
        lap1_percentage = lap1["Distance"] / lap1["Distance"].max()
        lap2_percentage = lap2["Distance"] / lap2["Distance"].max()

        common_progress = np.linspace(0, 1, num=500)

        lap1_time_interp = interp1d(lap1_percentage, lap1_time_seconds, kind="linear", fill_value="extrapolate")
        lap2_time_interp = interp1d(lap2_percentage, lap2_time_seconds, kind="linear", fill_value="extrapolate")

        lap1_time_common = lap1_time_interp(common_progress)
        lap2_time_common = lap2_time_interp(common_progress)

        time_gap = lap1_time_common - lap2_time_common

        # Delta time comparison
        axs[2].plot(common_progress * 100, time_gap, color="white")
        axs[2].set_ylabel(f"{driver1} vs {driver2}")
        axs[2].axhline(0, color="gray", linestyle="--", alpha=0.7)
        axs[2].grid(True, linestyle="--", alpha=0.5)
        axs[2].set_xlabel("Distance (%)")

        # Plotting
        plt.suptitle(
            f"{session.event['EventName']} {session.event.year} {session.name}\n"
            f"Lap Time Comparison: {driver1} vs {driver2}\n"
            f"{driver1}: {formatted_time1} | {driver2}: {formatted_time2}",
            fontsize=14
        )
        plt.tight_layout()

    return fig

# Plot 3: Maximum Speeds Compared to Best Lap Times
def plot_max_speeds(session):
    drivers = session.laps["Driver"].unique()
    max_speeds = {}
    best_laps = {}
    team_colors = {}

    for driver in drivers:
        laps = session.laps.pick_drivers(driver)
        if laps.empty:
            continue  # Skip drivers with no laps
        
        max_speeds[driver] = laps["SpeedST"]
        
        fastest_lap = laps.pick_fastest()
        if fastest_lap is not None:
            best_laps[driver] = fastest_lap["LapTime"]
        else:
            st.warning(f"No valid fastest lap for **{driver}**.")
            continue  

        team = laps.iloc[0]["Team"]
        team_colors[driver] = TEAM_COLORS.get(team, "gray")

    valid_drivers = list(best_laps.keys())
    delta_times = [(best_laps[drv] - min(best_laps.values())).total_seconds() for drv in valid_drivers]
    speeds = [max_speeds[drv].max() for drv in valid_drivers]
    colors = [team_colors[drv] for drv in valid_drivers]

    # Create figure for the plot
    fig, ax = plt.subplots(figsize=(16, 9), dpi=1000)
    ax.scatter(delta_times, speeds, color=colors, edgecolors="white", s=100)

    # Annotate each point with the driver's name
    for drv, x, y, color in zip(valid_drivers, delta_times, speeds, colors):
        ax.text(x, y, drv, fontsize=9, color=color, ha="left", va="bottom")

    # Plotting
    ax.set_xlabel("Delta Time (s)")
    ax.set_ylabel("Top Speed (km/h)")
    ax.set_title(f"{session.event['EventName']} {session.event.year} {session.name}\n" 
                 "Maximum Speeds vs Best Lap Time",fontsize=14)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.style.use("dark_background")
    plt.tight_layout()

    return fig

# Plot 4: Track Dominance
def plot_track_dominance(session, driver1, driver2):
    plt.style.use("dark_background")
    lapdata1 = session.laps.pick_drivers(driver1).pick_fastest()
    lapdata2 = session.laps.pick_drivers(driver2).pick_fastest()

    lap1 = lapdata1.get_telemetry().add_distance()
    lap2 = lapdata2.get_telemetry().add_distance()

    driver1_team = lapdata1["Team"]
    driver2_team = lapdata2["Team"]

    color_driver1 = TEAM_COLORS.get(driver1_team, 'gray')
    color_driver2 = TEAM_COLORS.get(driver2_team, 'gray')

    # Synchronize distance for both drivers
    max_distance = min(lap1['Distance'].max(), lap2['Distance'].max())
    lap1 = lap1[lap1['Distance'] <= max_distance]
    lap2 = lap2[lap2['Distance'] <= max_distance]

    # Define distance grid
    n_subsectors = 25
    sector_bounds = np.linspace(0, max_distance, n_subsectors + 1)

    # Interpolate telemetry
    lap1_interp = {}
    lap2_interp = {}
    for var in ['X', 'Y', 'Speed']:
        interp1 = interp1d(lap1['Distance'], lap1[var], kind='linear', fill_value='extrapolate')
        interp2 = interp1d(lap2['Distance'], lap2[var], kind='linear', fill_value='extrapolate')
        lap1_interp[var] = interp1
        lap2_interp[var] = interp2

    # Create figure
    fig = plt.figure(figsize=(16, 9), dpi=300)
    spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[4, 1], figure=fig)
    ax_track = fig.add_subplot(spec[0])
    ax_legend = fig.add_subplot(spec[1])

    # Plot by subsectors
    for i in range(n_subsectors):
        d_start = sector_bounds[i]
        d_end = sector_bounds[i+1]
        
        # Fine grid inside subsector
        fine_distance = np.linspace(d_start, d_end, 50)

        # Average speed in this subsector
        avg_speed1 = lap1_interp['Speed'](fine_distance).mean()
        avg_speed2 = lap2_interp['Speed'](fine_distance).mean()

        faster_driver = driver1 if avg_speed1 > avg_speed2 else driver2
        color = color_driver1 if faster_driver == driver1 else color_driver2

        # Coordinates
        x = lap1_interp['X'](fine_distance) if faster_driver == driver1 else lap2_interp['X'](fine_distance)
        y = lap1_interp['Y'](fine_distance) if faster_driver == driver1 else lap2_interp['Y'](fine_distance)

        ax_track.plot(x, y, color=color, linewidth=2)

    # Start marker
    ax_track.plot(lap1['X'].iloc[0], lap1['Y'].iloc[0], marker='.', color='white', markersize=8, zorder=10)
    ax_track.text(lap1['X'].iloc[0], lap1['Y'].iloc[0], "Start", fontsize=9, ha='left', va='bottom', color='white', zorder=11)

    # Corners
    circuit_info = session.get_circuit_info()
    for _, corner in circuit_info.corners.iterrows():
        number = corner["Number"]
        x = corner["X"]
        y = corner["Y"]
        ax_track.text(x, y, str(number), fontsize=8, color='black', ha='center', va='center',
                      bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2'))

    # Plotting
    ax_track.set_xticks([])
    ax_track.set_yticks([])
    for spine in ax_track.spines.values():
        spine.set_visible(True)
        spine.set_color('white')
        spine.set_linewidth(1.5)

    ax_legend.axis('off')  # Hide axis
    lap_time1 = lapdata1["LapTime"].total_seconds()
    lap_time2 = lapdata2["LapTime"].total_seconds()

    def format_time(t):
        minutes = int(t // 60)
        seconds = int(t % 60)
        millis = int((t - int(t)) * 1000)
        return f"{minutes}:{seconds:02}.{millis:03}"

    legend_elements = [
        Patch(facecolor=color_driver1, label=f"{driver1}\nS1: {lapdata1['Sector1Time'].total_seconds():.3f}s\nS2: {lapdata1['Sector2Time'].total_seconds():.3f}s\nS3: {lapdata1['Sector3Time'].total_seconds():.3f}s"),
        Patch(facecolor=color_driver2, label=f"{driver2}\nS1: {lapdata2['Sector1Time'].total_seconds():.3f}s\nS2: {lapdata2['Sector2Time'].total_seconds():.3f}s\nS3: {lapdata2['Sector3Time'].total_seconds():.3f}s"),
    ]

    ax_legend.legend(
        handles=legend_elements,
        loc='center',
        title="Sector Times",
        fontsize=10,
        title_fontsize=11,
        framealpha=0.95,
        borderpad=1.2,
        labelspacing=1.2
    )

    fig.suptitle(f"{session.event['EventName']} {session.event.year} {session.name}\n"
                 f"Track Dominance: {driver1} vs {driver2}\n"
                 f"{driver1}: {format_time(lap_time1)} | {driver2}: {format_time(lap_time2)}",
                 fontsize=14)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    gui.run_gui()
