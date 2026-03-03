import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt

# --- Setup ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide")
geolocator = Nominatim(user_agent="vedic_astro_app")

# Constants for Stability
AYANAMSA_MAP = {"Lahiri": 1, "Raman": 3, "KP": 5, "Pushya": 41}
PLANETS = {"Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2, "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 11}

# --- Visual Chart Function ---
def draw_north_indian_chart(house_planets, lagna_rashi):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.axis('off')
    # Draw Lines
    ax.plot([0, 400, 400, 0, 0], [0, 0, 400, 400, 0], color='black') # Square
    ax.plot([0, 400], [0, 400], color='black'); ax.plot([0, 400], [400, 0], color='black') # Diagonals
    ax.plot([200, 400, 200, 0, 200], [400, 200, 0, 200, 400], color='black') # Diamond
    
    # House Coordinates
    centers = [(200, 300), (100, 350), (50, 300), (150, 200), (50, 100), (100, 50), 
               (200, 100), (300, 50), (350, 100), (250, 200), (350, 300), (300, 350)]
    
    for i in range(12):
        r_num = (lagna_rashi + i - 1) % 12 + 1
        ax.text(centers[i][0], centers[i][1]-20, str(r_num), color='red', fontsize=10, ha='center')
        p_list = "\n".join(house_planets[i])
        ax.text(centers[i][0], centers[i][1], p_list, fontsize=9, ha='center', fontweight='bold')
    return fig

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📍 Details")
    # FIXED: Added min/max years so she can go beyond 2016
    dob = st.date_input("Date of Birth", 
                        value=datetime(2000, 1, 1),
                        min_value=datetime(1900, 1, 1),
                        max_value=datetime(2100, 12, 31))
    tob = st.time_input("Time of Birth", step=60)
    city = st.text_input("City", "Mumbai")
    ayan = st.selectbox("Ayanamsa", list(AYANAMSA_MAP.keys()))

# --- Main Logic ---
if st.button("Generate Patrika"):
    # 1. Location & Time
    loc = geolocator.geocode(city)
    lat, lon = (loc.latitude, loc.longitude) if loc else (19.07, 72.87)
    utc_dt = datetime.combine(dob, tob) - timedelta(hours=5.5)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
    
    # 2. Calculations
    swe.set_sid_mode(AYANAMSA_MAP[ayan])
    flags = swe.FLG_
