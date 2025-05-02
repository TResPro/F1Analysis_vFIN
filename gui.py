import streamlit as st
import f1_analysis
import io
import base64

def on_load_session(mode, year, grand_prix, session_type, driver1, driver2):
    from f1_analysis import TEAM_COLORS

    if not driver1 or not driver2:
        st.error("⚠️ Please enter both driver names.")
        return
    
    # Show loading spinner while loading the session and generating plots
    with st.spinner("⏳ Loading session data and generating plots..."):
        session = f1_analysis.load_session(mode, year, grand_prix, session_type)

        if session:
            st.toast("✅ Session loaded!", icon="📂")

            if session_type == "Qualifying":
                fig = f1_analysis.plot_best_laps(session)
                show_fig_with_download('🏎️ Best Lap Per Team', fig, 'best_lap_per_team_Q')

                fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
                show_fig_with_download('📈 Lap Time Comparison', fig, 'lap_time_comparison_Q')

                fig = f1_analysis.plot_track_dominance(session, driver1, driver2)
                show_fig_with_download('🏁 Track Dominance', fig, 'track_dominance_Q')

                fig = f1_analysis.plot_max_speeds(session)
                show_fig_with_download('🚀 Max Speeds vs Lap Time', fig, 'max_speeds_vs_laptime_Q')

            elif session_type == "Sprint Qualifying":
                fig = f1_analysis.plot_best_laps(session)
                show_fig_with_download('🏎️ Best Lap Per Team', fig, 'best_lap_per_team_SQ')

                fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
                show_fig_with_download('📈 Lap Time Comparison', fig, 'lap_time_comparison_SQ')

                fig = f1_analysis.plot_track_dominance(session, driver1, driver2)
                show_fig_with_download('🏁 Track Dominance', fig, 'track_dominance_SQ')

                fig = f1_analysis.plot_max_speeds(session)
                show_fig_with_download('🚀 Max Speeds vs Lap Time', fig, 'max_speeds_vs_laptime_SQ')

            elif session_type == "Race":
                fig = f1_analysis.plot_stint_comparison(session, [driver1, driver2], TEAM_COLORS)
                show_fig_with_download('🏁 Stint Comparison', fig, 'stint_comparison_R')

                fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
                show_fig_with_download('📊 Lap Time Distribution', fig, 'lap_time_distribution_R')

            elif session_type == "Sprint Race":
                fig = f1_analysis.plot_stint_comparison(session, [driver1, driver2], TEAM_COLORS)
                show_fig_with_download('🏁 Stint Comparison', fig, 'stint_comparison_SR')

                fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
                show_fig_with_download('📊 Lap Time Distribution', fig, 'lap_time_distribution_SR')

            elif session_type in ["FP1", "FP2", "FP3"]:
                fig = f1_analysis.plot_best_laps(session)
                show_fig_with_download('🏎️ Best Lap Per Team', fig, 'best_lap_per_team_FP')

                fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
                show_fig_with_download('📊 Lap Time Distribution', fig, 'lap_time_distribution_FP')

                fig = f1_analysis.plot_max_speeds(session)
                show_fig_with_download('🚀 Max Speeds vs Lap Time', fig, 'max_speeds_vs_laptime_FP')

                fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
                if fig is not None:
                    show_fig_with_download('📈 Lap Time Comparison', fig, 'lap_time_comparison_Q')

        st.success("✅ All plots generated successfully!")


# Start Streamlit App
def run_streamlit_app():
    st.set_page_config(page_title="F1 Analysis", layout="centered")

    # Sidebar for How to Use
    with st.sidebar:
        st.header("ℹ️ How to Use")
        st.info(
            """
            - Select the **year**, **Grand Prix**, and **session**.
            - Enter **driver codes** (e.g., 'VER', 'LEC', 'NOR').
            - Press **Load Session** to see telemetry comparisons.
            - You can change the **background theme** by clicking on the three dotted point in the top-right corner
            """,
            icon="🛠️"
        )
        st.markdown("---")
        st.markdown("Made with passion for F1 fans.<br>📩Contact Me formulatelemetryinfo@gmail.com", unsafe_allow_html=True)

    # Main title
    st.title("🏎️ F1 Analysis®")
    st.markdown("Choose your race weekend, session, year, and drivers — then dive into the telemetry and start uncovering the secrets of speed!<br> ---", unsafe_allow_html=True)

    # Centered form layout
    st.markdown("## Select Session Details", unsafe_allow_html=True)
    with st.form("session_form"):
        col1, col2 = st.columns(2)

        with col1:
            mode = st.selectbox("Select Mode:", ["Grand Prix"], index=0)
            year = st.selectbox("Select Year", ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"])
            session_type = st.selectbox("Select Session", ["FP1", "FP2", "FP3", "Sprint Qualifying", "Qualifying", "Sprint Race","Race"])

        with col2:
            grand_prix = st.selectbox(
                "Select GP",
                [
                    "Australia", "Saudi Arabia", "Bahrain", "Japan", "China", "Miami", "Emilia Romagna",
                    "Monaco", "Canada", "Spain", "Austria", "Silverstone", "Hungary", "Belgium",
                    "Netherlands", "Italy", "Azerbaijan", "Singapore", "Austin", "Mexico",
                    "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
                ]
            )
            driver1 = st.text_input("Driver 1", placeholder="e.g., VER")
            driver2 = st.text_input("Driver 2", placeholder="e.g., LEC")

        # Button in the form
        submitted = st.form_submit_button("🚀 Load Session")
    if submitted:
        on_load_session(mode, year, grand_prix, session_type, driver1, driver2)

# Faster byte conversion
def get_fig_bytes(_fig):
    buf = io.BytesIO()
    _fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf.read()

# Download button
def show_fig_with_download(title, fig, filename):
    fig_bytes = get_fig_bytes(fig)
    b64 = base64.b64encode(fig_bytes).decode()

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 6px;">
            <h3 style="margin: 0;">{title}</h3>
            <a href="data:file/png;base64,{b64}" download="{filename}.png" 
               style="
                   background-color: transparent;
                   padding: 4px 6px;
                   border: 0.5px solid #666666;
                   border-radius: 6px;
                   text-decoration: none;
                   font-size: 16px;
                   color: black;
                   position: relative;
                   top: -2px;
               " title="Download figure">
                📥
            </a>
        </div>
    """, unsafe_allow_html=True)

    st.pyplot(fig, use_container_width=True)

if __name__ == "__main__":
    run_streamlit_app()
