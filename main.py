import streamlit as st, json
from datetime import date, datetime
from controller import Controller

drivers = {
    "ALB": "Alexander Albon",
    "ALO": "Fernando Alonso",
    "ANT": "Kimi Antonelli",
    "BEA": "Oliver Bearman",
    "BOR": "Gabriel Bortoleto",
    "COL": "Franco Colapinto",
    "GAS": "Pierre Gasly",
    "HAD": "Isack Hadjar",
    "HAM": "Lewis Hamilton",
    "HUL": "Nico Hulkenberg",
    "LAW": "Liam Lawson",
    "LEC": "Charles Leclerc",
    "NOR": "Lando Norris",
    "OCO": "Esteban Ocon",
    "PIA": "Oscar Piastri",
    "RUS": "George Russell",
    "SAI": "Carlos Sainz",
    "STR": "Lance Stroll",
    "TSU": "Yuki Tsunoda",
    "VER": "Max Verstappen"
}


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
        st.metric("Selected Track", selected_track)
    
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
                
                # Add custom CSS for enhanced styling
                st.markdown("""
                <style>
                .prediction-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px;
                    padding: 25px;
                    margin: 20px 0;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                
                .ranking-title {
                    text-align: center;
                    color: white;
                    font-size: 2.2em;
                    font-weight: bold;
                    margin-bottom: 25px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }
                
                .podium-section {
                    background: rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    backdrop-filter: blur(10px);
                }
                
                .podium-driver {
                    display: flex;
                    align-items: center;
                    padding: 15px 20px;
                    margin: 8px 0;
                    border-radius: 10px;
                    font-size: 1.2em;
                    font-weight: 600;
                    transition: transform 0.3s ease;
                }
                
                .podium-driver:hover {
                    transform: translateX(10px);
                }
                
                .position-1 {
                    background: linear-gradient(135deg, #FFD700, #FFA500);
                    color: #333;
                    box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
                }
                
                .position-2 {
                    background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
                    color: #333;
                    box-shadow: 0 5px 15px rgba(192, 192, 192, 0.4);
                }
                
                .position-3 {
                    background: linear-gradient(135deg, #CD7F32, #8B4513);
                    color: white;
                    box-shadow: 0 5px 15px rgba(205, 127, 50, 0.4);
                }
                
                .regular-positions {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .driver-position {
                    display: flex;
                    align-items: center;
                    padding: 12px 18px;
                    margin: 5px 0;
                    background: rgba(255,255,255,0.15);
                    border-radius: 8px;
                    color: white;
                    font-size: 1.1em;
                    font-weight: 500;
                    border-left: 4px solid #00d4ff;
                    backdrop-filter: blur(5px);
                    transition: all 0.3s ease;
                }
                
                .driver-position:hover {
                    background: rgba(255,255,255,0.25);
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                
                .position-medal {
                    font-size: 1.5em;
                    margin-right: 15px;
                    min-width: 40px;
                }
                
                .driver-name {
                    flex-grow: 1;
                }
                
                .section-divider {
                    height: 2px;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
                    margin: 20px 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Display results with enhanced styling
                st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
                st.markdown('<div class="ranking-title">🏆 Predicted Race Ranking</div>', unsafe_allow_html=True)
                
                # Create two columns for the entire ranking
                col1, col2 = st.columns(2)
                
                # Split all drivers into two columns
                mid_point = (len(ranking) + 1) // 2
                col1_drivers = ranking[:mid_point]
                col2_drivers = ranking[mid_point:]
                
                # Column 1
                with col1:
                    for i, driver in enumerate(col1_drivers):
                        position = i + 1
                        medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                        
                        if position <= 3:
                            position_class = f"position-{position}"
                            st.markdown(f'''
                            <div class="podium-driver {position_class}">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                                <div style="font-size: 0.9em; opacity: 0.8;">P{position}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                            <div class="driver-position">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                
                # Column 2
                with col2:
                    for i, driver in enumerate(col2_drivers):
                        position = i + 1 + len(col1_drivers)
                        medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                        
                        if position <= 3:
                            position_class = f"position-{position}"
                            st.markdown(f'''
                            <div class="podium-driver {position_class}">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                                <div style="font-size: 0.9em; opacity: 0.8;">P{position}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                            <div class="driver-position">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error making prediction: {str(e)}")

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
                
                # Add custom CSS for enhanced styling
                st.markdown("""
                <style>
                .prediction-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px;
                    padding: 25px;
                    margin: 20px 0;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                
                .ranking-title {
                    text-align: center;
                    color: white;
                    font-size: 2.2em;
                    font-weight: bold;
                    margin-bottom: 25px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }
                
                .podium-section {
                    background: rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    backdrop-filter: blur(10px);
                }
                
                .podium-driver {
                    display: flex;
                    align-items: center;
                    padding: 15px 20px;
                    margin: 8px 0;
                    border-radius: 10px;
                    font-size: 1.2em;
                    font-weight: 600;
                    transition: transform 0.3s ease;
                }
                
                .podium-driver:hover {
                    transform: translateX(10px);
                }
                
                .position-1 {
                    background: linear-gradient(135deg, #FFD700, #FFA500);
                    color: #333;
                    box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
                }
                
                .position-2 {
                    background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
                    color: #333;
                    box-shadow: 0 5px 15px rgba(192, 192, 192, 0.4);
                }
                
                .position-3 {
                    background: linear-gradient(135deg, #CD7F32, #8B4513);
                    color: white;
                    box-shadow: 0 5px 15px rgba(205, 127, 50, 0.4);
                }
                
                .regular-positions {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .driver-position {
                    display: flex;
                    align-items: center;
                    padding: 12px 18px;
                    margin: 5px 0;
                    background: rgba(255,255,255,0.15);
                    border-radius: 8px;
                    color: white;
                    font-size: 1.1em;
                    font-weight: 500;
                    border-left: 4px solid #00d4ff;
                    backdrop-filter: blur(5px);
                    transition: all 0.3s ease;
                }
                
                .driver-position:hover {
                    background: rgba(255,255,255,0.25);
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                
                .position-medal {
                    font-size: 1.5em;
                    margin-right: 15px;
                    min-width: 40px;
                }
                
                .driver-name {
                    flex-grow: 1;
                }
                
                .section-divider {
                    height: 2px;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
                    margin: 20px 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Create two columns for the entire ranking
                col1, col2 = st.columns(2)
                
                # Split all drivers into two columns
                mid_point = (len(ranking) + 1) // 2
                col1_drivers = ranking[:mid_point]
                col2_drivers = ranking[mid_point:]
                
                # Column 1
                with col1:
                    for i, driver in enumerate(col1_drivers):
                        position = i + 1
                        medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                        
                        if position <= 3:
                            position_class = f"position-{position}"
                            st.markdown(f'''
                            <div class="podium-driver {position_class}">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                                <div style="font-size: 0.9em; opacity: 0.8;">P{position}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                            <div class="driver-position">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                
                # Column 2
                with col2:
                    for i, driver in enumerate(col2_drivers):
                        position = i + 1 + len(col1_drivers)
                        medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                        
                        if position <= 3:
                            position_class = f"position-{position}"
                            st.markdown(f'''
                            <div class="podium-driver {position_class}">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                                <div style="font-size: 0.9em; opacity: 0.8;">P{position}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''
                            <div class="driver-position">
                                <div class="position-medal">{medal}</div>
                                <div class="driver-name">{drivers[driver]}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error making prediction: {str(e)}")

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
            # Add custom CSS for enhanced styling
            st.markdown("""
            <style>
            .prediction-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .ranking-title {
                text-align: center;
                color: white;
                font-size: 2.2em;
                font-weight: bold;
                margin-bottom: 25px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            
            .podium-section {
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                backdrop-filter: blur(10px);
            }
            
            .podium-driver {
                display: flex;
                align-items: center;
                padding: 15px 20px;
                margin: 8px 0;
                border-radius: 10px;
                font-size: 1.2em;
                font-weight: 600;
                transition: transform 0.3s ease;
            }
            
            .podium-driver:hover {
                transform: translateX(10px);
            }
            
            .position-1 {
                background: linear-gradient(135deg, #FFD700, #FFA500);
                color: #333;
                box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
            }
            
            .position-2 {
                background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
                color: #333;
                box-shadow: 0 5px 15px rgba(192, 192, 192, 0.4);
            }
            
            .position-3 {
                background: linear-gradient(135deg, #CD7F32, #8B4513);
                color: white;
                box-shadow: 0 5px 15px rgba(205, 127, 50, 0.4);
            }
            
            .regular-positions {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 20px;
            }
            
            .driver-position {
                display: flex;
                align-items: center;
                padding: 12px 18px;
                margin: 5px 0;
                background: rgba(255,255,255,0.15);
                border-radius: 8px;
                color: white;
                font-size: 1.1em;
                font-weight: 500;
                border-left: 4px solid #00d4ff;
                backdrop-filter: blur(5px);
                transition: all 0.3s ease;
            }
            
            .driver-position:hover {
                background: rgba(255,255,255,0.25);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .position-medal {
                font-size: 1.5em;
                margin-right: 15px;
                min-width: 40px;
            }
            
            .driver-name {
                flex-grow: 1;
            }
            
            .section-divider {
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
                margin: 20px 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display results with enhanced styling
            st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
            st.markdown('<div class="ranking-title">🏆 Predicted Race Ranking</div>', unsafe_allow_html=True)
            
            # Create two columns for the entire ranking
            col1, col2 = st.columns(2)
            
            # Split all drivers into two columns
            mid_point = (len(ranking) + 1) // 2
            col1_drivers = ranking.iloc[:mid_point]
            col2_drivers = ranking.iloc[mid_point:]
            
            # Column 1
            with col1:
                for i, row in col1_drivers.iterrows():
                    position = i + 1
                    medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                    
                    if position <= 3:
                        position_class = f"position-{position}"
                        st.markdown(f'''
                        <div class="podium-driver {position_class}">
                            <div class="position-medal">{medal}</div>
                            <div class="driver-name">{drivers[row.Code]} - {row.Points}</div>
                            <div style="font-size: 0.9em; opacity: 0.8;">P{position}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="driver-position">
                            <div class="position-medal">{medal}</div>
                            <div class="driver-name">{drivers[row.Code]} - {row.Points}</div>
                        </div>
                        ''', unsafe_allow_html=True)
            
            # Column 2
            with col2:
                for i, row in col2_drivers.iterrows():
                    position = i + 1 
                    medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
                    
                    if position <= 3:
                        position_class = f"position-{position}"
                        st.markdown(f'''
                        <div class="podium-driver {position_class}">
                            <div class="position-medal">{medal}</div>
                            <div class="driver-name">{drivers[row.Code]}</div>
                            <div style="font-size: 0.9em; opacity: 0.8;">P{position}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="driver-position">
                            <div class="position-medal">{medal}</div>
                            <div class="driver-name">{drivers[row.Code]} - {row.Points}</div>
                        </div>
                        ''', unsafe_allow_html=True)
            
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
