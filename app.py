import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt

# --- Setup ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide")
geolocator = Nominatim(user_agent="vedic_astro_app_v4")

# Constants for Stability
AYANAMSA_MAP = {"Lahiri": 1, "Raman": 3, "KP": 5, "Pushya": 41}
PLANETS_MAP = {"Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2, "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 11}

# --- Visual Chart Function ---
def draw_north_indian_chart(house_data, lagna_rashi):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.axis('off')
    
    # Draw Lines (North Indian Style)
    ax.plot([0, 400, 400, 0, 0], [0, 0, 400, 400, 0], color='black', lw=2) # Outer Square
    ax.plot([0, 400], [0, 400], color='black', lw=1); ax.plot([0, 400], [400, 0], color='black', lw=1) # Diagonals
    ax.plot([200, 400, 200, 0, 200], [400, 200, 0, 200, 400], color='black', lw=1) # Inner Diamond
    
    # House Coordinates for placing text
    centers = [
        (200, 300), (100, 350), (50, 300), (150, 200), (50, 100), (100, 50), 
        (200, 100), (300, 50), (350, 100), (250, 200), (350, 300), (300, 350)
    ]
    
    for i in range(12):
        # Calculate Rashi Number for each house
        r_num = (lagna_rashi + i - 1) % 12 + 1
        # Place Rashi Number
        ax.text(centers[i][0], centers[i][1]-30, str(r_num), color='red', fontsize=12, ha='center')
        # Place Planets
        p_list = "\n".join(house_data[i])
        ax.text(centers[i][0], centers[i][1], p_list, fontsize=10, ha='center', va='center', fontweight='bold')
    
    return fig

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📍 Birth Details")
    # Calendar set to 1900-2100 to fix your year issue
    dob = st.date_input("Date of Birth", 
                        value=datetime(1990, 1, 1),
                        min_value=datetime(1900, 1, 1), 
                        max_value=datetime(2100, 12, 31))
    tob = st.time_input("Time of Birth", step=60)
    city = st.text_input("City", "Mumbai, India")
    ayan = st.selectbox("Ayanamsa", list(AYANAMSA_MAP.keys()))

# --- Main Logic ---
if st.button("Generate Accurate Patrika"):
    try:
        # 1. Location & Time
        location = geolocator.geocode(city)
        lat, lon = (location.latitude, location.longitude) if location else (19.0760, 72.8777)
        
        # Convert to UTC (Assuming IST 5.5)
        utc_dt = datetime.combine(dob, tob) - timedelta(hours=5, minutes=30)
        
        # Calculate Julian Day
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
        
        # 2. Set Calculation Flags (FIXED LINE)
        swe.set_sid_mode(AYANAMSA_MAP[ayan])
        calc_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        
        # 3. Calculate Lagna (Ascendant)
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', calc_flags)
        lagna_lon = ascmc[0]
        lagna_rashi = int(lagna_lon / 30) + 1
        
        # 4. Calculate Planets & Assign to Houses
        house_data = [[] for _ in range(12)]
        planet_results = []
        
        for p_name, p_id in PLANETS_MAP.items():
            res = swe.calc_ut(jd, p_id, calc_flags)
            lon_p = res[0][0]
            p_rashi = int(lon_p / 30) + 1
            # Determine house index relative to Lagna (0-11)
            h_idx = (p_rashi - lagna_rashi) % 12
            house_data[h_idx].append(p_name[:2])
            planet_results.append({"Planet": p_name, "Rashi": p_rashi, "Degree": f"{lon_p%30:.2f}°"})

        # 5. UI Layout
        st.success(f"Generated Patrika for {city}")
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.subheader("🗺️ North Indian Lagna Chart (D1)")
            st.pyplot(draw_north_indian_chart(house_data, lagna_rashi))
            
        with col2:
            st.subheader("🪐 Planetary Degrees")
            st.table(pd.DataFrame(planet_results))
            
    except Exception as e:
        st.error(f"Something went wrong: {e}")
