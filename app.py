import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- Setup ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide", page_icon="🕉️")
geolocator = Nominatim(user_agent="vedic_astro_app_v7")

# Constants
AYANAMSA_MAP = {"Lahiri": 1, "Raman": 3, "KP": 5, "Pushya": 41}
PLANETS_MAP = {"Sun": 0, "Moon": 1, "Mars": 4, "Mercury": 2, "Jupiter": 5, "Venus": 3, "Saturn": 6, "Rahu": 11}

def draw_north_indian_chart(house_data, lagna_rashi, person_name):
    # Set facecolor to white for clean WhatsApp sharing
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='white')
    ax.set_xlim(0, 400); ax.set_ylim(0, 400); ax.axis('off')
    
    # Draw Lines
    ax.plot([0, 400, 400, 0, 0], [0, 0, 400, 400, 0], color='black', lw=2)
    ax.plot([0, 400], [0, 400], color='black', lw=1); ax.plot([0, 400], [400, 0], color='black', lw=1)
    ax.plot([200, 400, 200, 0, 200], [400, 200, 0, 200, 400], color='black', lw=1)
    
    # House Centers
    centers = [(200, 300), (100, 350), (50, 300), (150, 200), (50, 100), (100, 50), 
               (200, 100), (300, 50), (350, 100), (250, 200), (350, 300), (300, 350)]
    
    for i in range(12):
        r_num = (lagna_rashi + i - 1) % 12 + 1
        ax.text(centers[i][0], centers[i][1]-35, str(r_num), color='red', fontsize=12, ha='center')
        p_list = "\n".join(house_data[i])
        ax.text(centers[i][0], centers[i][1], p_list, fontsize=11, ha='center', va='center', fontweight='bold')
    
    plt.title(f"Patrika: {person_name}", fontsize=14, pad=20)
    return fig

# --- Sidebar ---
with st.sidebar:
    st.header("📍 Birth Details")
    p_name = st.text_input("Name", "New Chart")
    dob = st.date_input("Date of Birth", value=datetime(1990, 1, 1), min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31))
    tob_str = st.text_input("Time (HH:MM) - 24hr format", value="12:00")
    city = st.text_input("City", "Mumbai, India")
    ayan = st.selectbox("Ayanamsa", list(AYANAMSA_MAP.keys()))
    st.info("Tip: Type the time directly for speed!")

# --- Main Logic ---
if st.button("Generate Patrika"):
    try:
        # Parse Time
        try:
            tob_parsed = datetime.strptime(tob_str, "%H:%M").time()
        except:
            st.error("Invalid Time Format. Use HH:MM (e.g. 14:30)")
            st.stop()

        # Geolocation
        location = geolocator.geocode(city)
        lat, lon = (location.latitude, location.longitude) if location else (19.0760, 72.8777)
        
        # UTC Conversion (IST 5.5)
        utc_dt = datetime.combine(dob, tob_parsed) - timedelta(hours=5, minutes=30)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
        
        # Calculate
        swe.set_sid_mode(AYANAMSA_MAP[ayan])
        calc_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', calc_flags)
        lagna_rashi = int(ascmc[0] / 30) + 1
        
        house_data = [[] for _ in range(12)]
        planet_results = []
        for p_name_key, p_id in PLANETS_MAP.items():
            res = swe.calc_ut(jd, p_id, calc_flags)
            lon_p = res[0][0]
            p_rashi = int(lon_p / 30) + 1
            h_idx = (p_rashi - lagna_rashi) % 12
            house_data[h_idx].append(p_name_key[:2]) # First 2 letters: "Su", "Mo"
            planet_results.append({"Planet": p_name_key, "Rashi": p_rashi, "Degree": f"{lon_p%30:.2f}°"})

        # --- Display Results ---
        st.success(f"Generated for {city}")
        col1, col2 = st.columns([1.2, 0.8])
        
        fig_final = draw_north_indian_chart(house_data, lagna_rashi, p_name)
        
        with col1:
            st.pyplot(fig_final)
            
            # --- PNG EXPORT LOGIC ---
            buf = io.BytesIO()
            fig_final.savefig(buf, format="png", bbox_inches='tight', dpi=200, facecolor='white')
            st.download_button(
                label="🖼️ Download PNG for WhatsApp",
                data=buf.getvalue(),
                file_name=f"{p_name}_Patrika.png",
                mime="image/png"
            )

        with col2:
            st.subheader("🪐 Degrees")
            st.table(pd.DataFrame(planet_results))
            
    except Exception as e:
        st.error(f"Error: {e}")
