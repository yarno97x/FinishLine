import streamlit as st
import pandas as pd, json
from datetime import date, datetime
from controller import Controller

# Page configuration
st.set_page_config(
    page_title="F1 Race Outcome Predictor",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .mode-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E8B57;
        margin-bottom: 1rem;
    }
    .prediction-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4ECDC4;
        margin: 1rem 0;
    }
    .driver-position {
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .subtitle {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize controller
@st.cache_resource
def load_controller():
    return Controller()

controller = load_controller()

# Main header
st.markdown('<h1 class="main-header">🏎️ FinishLine</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subtitle">F1 Race Outcome Predictor</h3>', unsafe_allow_html=True)

with open("data/links.json", "r", encoding="utf-8") as f:
    LINKS = json.load(f)

# F1 tracks list 
F1_TRACKS = {track:val['id'] for track, val in LINKS.items()}

# F1 drivers (2024 season)
F1_DRIVERS = [
    "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell",
    "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri",
    "Fernando Alonso", "Lance Stroll", "Esteban Ocon", "Oliver Bearman",
    "Alexander Albon", "Carlos Sainz", "Nico Hulkenberg", "Gabriel Bortoleto",
    "Liam Lawson", "Isack Hadjar", "Franco Colapinto", "Pierre Gasly"
]

# Sidebar for mode selection
st.sidebar.title("Prediction Mode")
prediction_mode = st.sidebar.radio(
    "Select prediction mode:",
    ["Pre-Qualifying", "Post-Qualifying", "Season Rankings"],
    help="Pre-Qualifying: Predict based on track only\nPost-Qualifying: Predict based on track, times, and grid positions\nSeason Projections: Predict season outcomes based on races left"
)

# Main content area
if prediction_mode == "Pre-Qualifying":
    st.markdown('<div class="mode-header">🏁 Pre-Qualifying Prediction</div>', unsafe_allow_html=True)
    
    # Track selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_track = st.selectbox(
            "Select F1 Track:",
            F1_TRACKS.keys(),
            index=0,
            help="Choose the track where the race will take place"
        )
    
    with col2:
        st.metric("Selected Track", selected_track.split()[-1])
    
    # Predict button
    if st.button("🔮 Predict Race Outcome", type="primary", use_container_width=True):
        with st.spinner("Analyzing track data and predicting race outcome..."):
            try:
                # Prepare input for pre-qualifying prediction
                prediction_input = {
                    "mode": "pre_qualifying",
                    "track": F1_TRACKS[selected_track]
                }
                
                # Get prediction from controller
                ranking = controller.predict(prediction_input)
                
                # Display results
                st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                st.subheader("🏆 Predicted Race Ranking")
                
                # Create two columns for better display
                col1, col2 = st.columns(2)
                
                for i, driver in enumerate(ranking):  # Show top 10
                    position = i + 1
                    medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                    
                    if position <= 10:
                        col1.markdown(f'<div class="driver-position">{position}. {driver}</div>', unsafe_allow_html=True)
                    else:
                        col2.markdown(f'<div class="driver-position">{position}. {driver}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                
            except Exception as e:
                st.error(f"Error during prediction: {str(e)}")

elif prediction_mode == "Post-Qualifying":  # Post-Qualifying mode
    st.markdown('<div class="mode-header">🏁 Post-Qualifying Prediction</div>', unsafe_allow_html=True)
    
    # Track selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_track = st.selectbox(
            "Select F1 Track:",
            F1_TRACKS.keys(),
            index=0,
            help="Choose the track where the race will take place"
        )
    
    with col2:
        st.metric("Selected Track", selected_track.split()[-1])

    if st.button("🔮 Predict Race Outcome", type="primary", use_container_width=True) and int(date.today().strftime("%j")) + 1 >= LINKS[selected_track]['day']:
        with st.spinner("Analyzing track data and predicting race outcome..."):
            try:
                # Prepare input for pre-qualifying prediction
                prediction_input = {
                    "mode": "post_qualifying",
                    "track": F1_TRACKS[selected_track],
                    "link": LINKS[selected_track]["url_quali"]
                }
                
                # Get prediction from controller
                ranking = controller.predict(prediction_input)
                
                # Display results
                st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                st.subheader("🏆 Predicted Race Ranking")
                
                # Create two columns for better display
                col1, col2 = st.columns(2)
                
                for i, driver in enumerate(ranking):  # Show top 10
                    position = i + 1
                    
                    if position <= 10:
                        col1.markdown(f'<div class="driver-position">{position}. {driver}</div>', unsafe_allow_html=True)
                    else:
                        col2.markdown(f'<div class="driver-position">{position}. {driver}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error during prediction: {str(e)}")
else:
    st.markdown('<div class="mode-header">🏁 Season Projections</div>', unsafe_allow_html=True)
    
    # Track selection
    col1, col2 = st.columns([2, 1])

    with st.spinner("Analyzing track data and predicting race outcome..."):
        try:
            # Prepare input for pre-qualifying prediction
            
            # Get prediction from controller
            ranking = controller.predict_season()
            
            # Display results
            st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
            st.subheader("🏆 Predicted Season Ranking")
            
            # Create two columns for better display
            col1, col2 = st.columns(2)
            
            for i, row in ranking.iterrows():  # Show top 10
                position = i + 1
                
                if position <= 10:
                    col1.markdown(f'<div class="driver-position">{position}. {row.Code} - {row.Points}</div>', unsafe_allow_html=True)
                else:
                    col2.markdown(f'<div class="driver-position">{position}. {row.Code} - {row.Points}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🏎️ F1 Race Outcome Predictor | "
    f"Powered by Machine Learning | {datetime.now().year}</div>",
    unsafe_allow_html=True
)
