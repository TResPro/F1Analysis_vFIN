import streamlit as st
import f1_analysis

# Load session from inputs
def on_load_session(mode, year, grand_prix, session_type, driver1, driver2):
    from f1_analysis import TEAM_COLORS
    if not driver1 or not driver2:
        st.error("Please enter both driver names.")
        return

    session = f1_analysis.load_session(mode, year, grand_prix, session_type)
    if session:
            if session_type == "Qualifying":
                # Call the plotting functions and use st.pyplot() to render the plots
                fig = f1_analysis.plot_best_laps(session)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_track_dominance(session, driver1, driver2)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_max_speeds(session)
                st.pyplot(fig)

            elif session_type == "Race":
                fig = f1_analysis.plot_stint_comparison(session, [driver1, driver2], TEAM_COLORS)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
                st.pyplot(fig)

            elif session_type in ["FP1", "FP2", "FP3"]:
                fig = f1_analysis.plot_best_laps(session)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_lap_comparison(session, driver1, driver2)
                st.pyplot(fig)
                
                fig = f1_analysis.plot_max_speeds(session)
                st.pyplot(fig)
# Start Streamlit App
def run_streamlit_app():
    st.set_page_config(page_title="F1 Telemetry Analyzer", layout="centered")

    # Title
    st.title("F1 ANALYSIS")

    # Mode Selection
    mode = st.selectbox("Select Mode:", ["Grand Prix"], index=0)

    # Year, Grand Prix, Session
    year = st.selectbox("Select Year", ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"])
    grand_prix = st.selectbox("Select GP", ["Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami", "Emilia Romagna", "Monaco", "Canada", "Spain", "Austria", "Silverstone", "Hungary", "Belgium", "Netherlands", "Italy", "Azerbaijan", "Singapore", "Austin", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"])
    session_type = st.selectbox("Select Session", ["FP1", "FP2", "FP3", "Qualifying", "Race"])

    # Driver Names
    driver1 = st.text_input("Driver 1", "Insert Driver 1")
    driver2 = st.text_input("Driver 2", "Insert Driver 2")

    # Load Session Button
    if st.button("Load Session"):
        on_load_session(mode, year, grand_prix, session_type, driver1, driver2)

if __name__ == "__main__":
    run_streamlit_app()
