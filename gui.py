import streamlit as st
import f1_analysis

# Load session from inputs
def on_load_session(mode, year, grand_prix, session_type, driver1, driver2):
    from f1_analysis import TEAM_COLORS
    if not driver1 or not driver2:
        st.error("⚠️ Please enter both driver names.")
        return

    session = f1_analysis.load_session(mode, year, grand_prix, session_type)
    if session:
        if session_type == "Qualifying":
            st.subheader('🏎️ Best Lap Per Team')
            fig = f1_analysis.plot_best_laps(session)
            st.pyplot(fig)

            st.subheader('📈 Lap Time Comparison')
            fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
            st.pyplot(fig)

            st.subheader('🛣️ Track Dominance')
            fig = f1_analysis.plot_track_dominance(session, driver1, driver2)
            st.pyplot(fig)

            st.subheader('🚀 Max Speeds vs Lap Time')
            fig = f1_analysis.plot_max_speeds(session)
            st.pyplot(fig)

        elif session_type == "Race":
            st.subheader('🏁 Stint Comparison')
            fig = f1_analysis.plot_stint_comparison(session, [driver1, driver2], TEAM_COLORS)
            st.pyplot(fig)

            st.subheader('📊 Lap Time Distribution')
            fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
            st.pyplot(fig)

        elif session_type in ["FP1", "FP2", "FP3"]:
            st.subheader('🏎️ Best Lap Per Team')
            fig = f1_analysis.plot_best_laps(session)
            st.pyplot(fig)

            st.subheader('📊 Lap Time Distribution')
            fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
            st.pyplot(fig)

            st.subheader('📈 Lap Time Comparison')
            fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
            st.pyplot(fig)

            st.subheader('🚀 Max Speeds vs Lap Time')
            fig = f1_analysis.plot_max_speeds(session)
            st.pyplot(fig)

# Start Streamlit App
def run_streamlit_app():
    st.set_page_config(page_title="F1 Telemetry Analyzer", layout="wide")

    # Header with "How to Use" Button
    col1, col2 = st.columns([10, 1])

    with col1:
        st.title("🏎️ F1 Telemetry Analyzer")

    with col2:
        how_to_use = st.toggle("ℹ️ How to Use", key="how_to_use_toggle")

    if how_to_use:
        st.info(
            """
            ### How to Use:
            - Select the **year**, **Grand Prix**, and **session**.
            - Enter **two drivers' names** exactly as in telemetry (e.g., 'VER', 'LEC').
            - Press **Load Session** to generate comparisons and visualizations.
            - Make sure the data exists for the session you selected!
            """,
            icon="🛠️"
        )

    # Divider
    st.markdown("---")

    # Centered layout
    st.markdown("## Select Session Details", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            mode = st.selectbox("Select Mode:", ["Grand Prix"], index=0)

        with col2:
            year = st.selectbox("Select Year", ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"])

        with col3:
            grand_prix = st.selectbox(
                "Select GP",
                [
                    "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami", "Emilia Romagna",
                    "Monaco", "Canada", "Spain", "Austria", "Silverstone", "Hungary", "Belgium",
                    "Netherlands", "Italy", "Azerbaijan", "Singapore", "Austin", "Mexico",
                    "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
                ]
            )

    col1, col2, col3 = st.columns(3)
    with col1:
        session_type = st.selectbox("Select Session", ["FP1", "FP2", "FP3", "Qualifying", "Race"])

    with col2:
        driver1 = st.text_input("Driver 1", placeholder="e.g., VER")

    with col3:
        driver2 = st.text_input("Driver 2", placeholder="e.g., LEC")

    # Load Session Button
    st.markdown("<br>", unsafe_allow_html=True)
    centered_button = st.columns([4, 2, 4])[1]
    with centered_button:
        if st.button("🚀 Load Session"):
            on_load_session(mode, year, grand_prix, session_type, driver1, driver2)

    # Footer
    st.markdown("---")
    st.caption("Made with ❤️ for F1 enthusiasts.")

if __name__ == "__main__":
    run_streamlit_app()
