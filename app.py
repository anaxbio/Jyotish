import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuration ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide", page_icon="🕉️")
geolocator = Nominatim(user_agent="vedic_astro_app_v3")

AYANAMSA_MAP = {"Lahiri": 1, "Raman": 3, "KP": 5, "Pushya": 41}
PLANETS = {"Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2, "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 11}

# --- Drawing Logic ---
def draw_north_indian_chart(house_data, lagna_rashi_num):
    """
    Draws a North Indian Style Chart using Matplotlib.
    house_data: A list of 12 lists, each containing planets in that house.
    lagna_rashi_num: The Rashi number (1-12) of the 1st house.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 400)
    ax.axis('off')

    # Draw Outer Square
    ax.plot([0, 400, 400, 0, 0], [0, 0, 400, 400, 0], color='black', lw=2)
    # Draw Diagonals
    ax.plot([0, 400], [0, 400], color='black', lw=1)
    ax.plot([0, 400], [400, 0], color='black', lw=1)
    # Draw Inner Diamond
    ax.plot([200, 400, 200, 0, 200], [400, 200, 0, 200, 400], color='black', lw=1)

    # House Center Coordinates (for placing text)
    centers = [
        (200, 280), (100, 350), (50, 300), (120, 200),
        (50, 100), (100, 50), (200, 120), (300, 50),
        (350, 100), (280, 200), (350, 300), (300, 350)
    ]
    
    # Rashi Number Positions (Small numbers in corners)
    rashi_pos = [
        (200, 220), (120, 300), (80, 300), (180, 200),
        (80, 100), (120, 80), (200, 180), (280, 80),
        (320, 100), (220, 200), (320, 300), (280, 320)
    ]

    for i in range(12):
        # 1. Draw Rashi Number
        r_num = (lagna_rashi_num + i - 1) % 12 + 1
        ax.text(rashi_pos[i][0], rashi_pos[i][1], str(r_num), fontsize=10, color='red', ha='center')
        
        # 2. Draw Planets
        p_text = "\n".join(house_data[i])
        ax.text(centers[i][0], centers[i][1], p_text, fontsize=9, ha='center', va='center', fontweight='bold')

    return fig

# --- Main App ---
st.sidebar.header("📍 Birth Details")
city = st.sidebar.text_input("City", "Mumbai")
dob = st.sidebar.date_input("Date")
tob = st.sidebar.time_input("Time", step=60)
ayan = st.sidebar.selectbox("Ayanamsa", list(AYANAMSA_MAP.keys()))

if st.sidebar.button("Generate"):
    # ... [Same coordinate/JD logic from previous steps] ...
    location = geolocator.geocode(city)
    lat, lon = (location.latitude, location.longitude) if location else (19.07, 72.87)
    utc_dt = datetime.combine(dob, tob) - timedelta(hours=5.5)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
    
    swe.set_sid_mode(AYANAMSA_MAP[ayan])
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    # Calculate Lagna
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags)
    lagna_lon = ascmc[0]
    lagna_rashi = int(lagna_lon / 30) + 1
    
    # Sort Planets into Houses
    house_planets = [[] for _ in range(12)]
    planet_rows = []
    
    for p_name, p_id in PLANETS.items():
        lon_p = swe.calc_ut(jd, p_id, flags)[0][0]
        # Calculate house relative to Lagna
        p_rashi = int(lon_p / 30) + 1
        h_idx = (p_rashi - lagna_rashi) % 12
        house_planets[h_idx].append(p_name[:2]) # Use "Su", "Mo", etc.
        planet_rows.append({"Planet": p_name, "Rashi": p_rashi, "Deg": f"{lon_p%30:.2f}°"})

    # Layout
    col1, col2 = st.columns([1, 1])
    with col1:
        st.pyplot(draw_north_indian_chart(house_planets, lagna_rashi))
    with col2:
        st.table(pd.DataFrame(planet_rows))
