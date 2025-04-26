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
            st.pyplot(fig, use_container_width=True)

            st.subheader('📈 Lap Time Comparison')
            fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
            st.pyplot(fig, use_container_width=True)

            st.subheader('🏁 Track Dominance')
            fig = f1_analysis.plot_track_dominance(session, driver1, driver2)
            st.pyplot(fig, use_container_width=True)

            st.subheader('🚀 Max Speeds vs Lap Time')
            fig = f1_analysis.plot_max_speeds(session)
            st.pyplot(fig, use_container_width=True)

        elif session_type == "Race":
            st.subheader('🏁 Stint Comparison')
            fig = f1_analysis.plot_stint_comparison(session, [driver1, driver2], TEAM_COLORS)
            st.pyplot(fig, use_container_width=True)

            st.subheader('📊 Lap Time Distribution')
            fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
            st.pyplot(fig, use_container_width=True)

        elif session_type in ["FP1", "FP2", "FP3"]:
            st.subheader('🏎️ Best Lap Per Team')
            fig = f1_analysis.plot_best_laps(session)
            st.pyplot(fig, use_container_width=True)

            st.subheader('📊 Lap Time Distribution')
            fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
            st.pyplot(fig, use_container_width=True)

            st.subheader('📈 Lap Time Comparison')
            fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
            st.pyplot(fig, use_container_width=True)

            st.subheader('🚀 Max Speeds vs Lap Time')
            fig = f1_analysis.plot_max_speeds(session)
            st.pyplot(fig, use_container_width=True)

# Start Streamlit App
def run_streamlit_app():
    st.set_page_config(page_title="F1 Telemetry Analyzer", layout="centered")

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
        st.caption("Made with passion for F1 fans.\nContact Me: formulatelemetryinfo@gmail.com")

    # Main title
    st.title("🏎️ F1 Telemetry Analyzer")
    st.markdown("---")

    # Centered form layout
    st.markdown("## Select Session Details", unsafe_allow_html=True)
    with st.form("session_form"):
        col1, col2 = st.columns(2)

        with col1:
            mode = st.selectbox("Select Mode:", ["Grand Prix"], index=0)
            year = st.selectbox("Select Year", ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"])
            session_type = st.selectbox("Select Session", ["FP1", "FP2", "FP3", "Qualifying", "Race"])

        with col2:
            grand_prix = st.selectbox(
                "Select GP",
                [
                    "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami", "Emilia Romagna",
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

if __name__ == "__main__":
    run_streamlit_app()
