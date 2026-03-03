import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt

# --- Setup ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide")
geolocator = Nominatim(user_agent="vedic_astro_app_v5")

# Constants
AYANAMSA_MAP = {"Lahiri": 1, "Raman": 3, "KP": 5, "Pushya": 41}
PLANETS_MAP = {"Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2, "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 11}

def draw_north_indian_chart(house_data, lagna_rashi):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.axis('off')
    ax.plot([0, 400, 400, 0, 0], [0, 0, 400, 400, 0], color='black', lw=2)
    ax.plot([0, 400], [0, 400], color='black', lw=1); ax.plot([0, 400], [400, 0], color='black', lw=1)
    ax.plot([200, 400, 200, 0, 200], [400, 200, 0, 200, 400], color='black', lw=1)
    centers = [(200, 300), (100, 350), (50, 300), (150, 200), (50, 100), (100, 50), (200, 100), (300, 50), (350, 100), (250, 200), (350, 300), (300, 350)]
    for i in range(12):
        r_num = (lagna_rashi + i - 1) % 12 + 1
        ax.text(centers[i][0], centers[i][1]-30, str(r_num), color='red', fontsize=12, ha='center')
        p_list = "\n".join(house_data[i])
        ax.text(centers[i][0], centers[i][1], p_list, fontsize=10, ha='center', va='center', fontweight='bold')
    return fig

# --- Sidebar ---
with st.sidebar:
    st.header("📍 Birth Details")
    dob = st.date_input("Date of Birth", value=datetime(1990, 1, 1), min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31))
    
    # CHANGED: Using text_input for faster typing
    tob_str = st.text_input("Time of Birth (HH:MM)", value="12:00", help="Type time in 24-hour format (e.g., 14:30)")
    
    city = st.text_input("City", "Mumbai, India")
    ayan = st.selectbox("Ayanamsa", list(AYANAMSA_MAP.keys()))

# --- Main Logic ---
if st.button("Generate Accurate Patrika"):
    try:
        # Validate Time Format
        try:
            tob_parsed = datetime.strptime(tob_str, "%H:%M").time()
        except ValueError:
            st.error("Please enter time in HH:MM format (e.g., 08:30 or 22:15)")
            st.stop()

        location = geolocator.geocode(city)
        lat, lon = (location.latitude, location.longitude) if location else (19.0760, 72.8777)
        
        utc_dt = datetime.combine(dob, tob_parsed) - timedelta(hours=5, minutes=30)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
        
        swe.set_sid_mode(AYANAMSA_MAP[ayan])
        calc_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', calc_flags)
        lagna_rashi = int(ascmc[0] / 30) + 1
        
        house_data = [[] for _ in range(12)]
        planet_results = []
        for p_name, p_id in PLANETS_MAP.items():
            res = swe.calc_ut(jd, p_id, calc_flags)
            lon_p = res[0][0]
            p_rashi = int(lon_p / 30) + 1
            h_idx = (p_rashi - lagna_rashi) % 12
            house_data[h_idx].append(p_name[:2])
            planet_results.append({"Planet": p_name, "Rashi": p_rashi, "Degree": f"{lon_p%30:.2f}°"})

        st.success(f"Generated Patrika for {city}")
        col1, col2 = st.columns([1.2, 0.8])
        with col1:
            st.pyplot(draw_north_indian_chart(house_data, lagna_rashi))
        with col2:
            st.table(pd.DataFrame(planet_results))
            
    except Exception as e:
        st.error(f"Something went wrong: {e}")
