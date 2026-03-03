import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd

# --- Configuration ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide")
geolocator = Nominatim(user_agent="vedic_astro_app")

# Ayanamsa IDs (Safe from AttributeError)
AYANAMSA_MAP = {
    "Lahiri (Chitra Paksha)": 1,
    "Raman": 3,
    "KP (Krishnamurti)": 5,
    "Pushya Paksha": 41
}

RASHI_NAMES = [
    "Aries (Mesha)", "Taurus (Vrishabha)", "Gemini (Mithuna)", 
    "Cancer (Karka)", "Leo (Simha)", "Virgo (Kanya)", 
    "Libra (Tula)", "Scorpio (Vrischika)", "Sagittarius (Dhanu)", 
    "Capricorn (Makara)", "Aquarius (Kumbha)", "Pisces (Meena)"
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE, # Traditional Vedic uses Mean Node for Rahu
}

def get_rashi_and_degree(total_degree):
    rashi_idx = int(total_degree / 30)
    degree_in_rashi = total_degree % 30
    minutes = (degree_in_rashi - int(degree_in_rashi)) * 60
    return RASHI_NAMES[rashi_idx], f"{int(degree_in_rashi)}° {int(minutes)}'"

# --- UI Layout ---
st.title("🕉️ Vedic Patrika Generator")
st.caption("Professional Grade Calculations for Vedic Students")

with st.sidebar:
    st.header("📍 Birth Details")
    name = st.text_input("Full Name", "New Chart")
    dob = st.date_input("Date of Birth", value=datetime(1980, 1, 1))
    tob = st.time_input("Time of Birth")
    
    city = st.text_input("Birth City", "Mumbai, India")
    ayanamsa_name = st.selectbox("Ayanamsa", list(AYANAMSA_MAP.keys()))
    
    st.divider()
    st.info("Uses Swiss Ephemeris (NASA-grade accuracy)")

# --- Main Logic ---
if st.button("Generate Accurate Chart"):
    try:
        # 1. Location Lookup
        loc = geolocator.geocode(city)
        if not loc:
            st.error("City not found. Defaulting to Mumbai.")
            lat, lon = 19.0760, 72.8777
        else:
            lat, lon = loc.latitude, loc.longitude
            st.success(f"Coordinates found for {city}")

        # 2. Time Conversion (Assuming IST +5.5 for India)
        # For a pro app, you'd calculate timezone offset dynamically, but 5.5 is standard for India.
        dt = datetime.combine(dob, tob)
        utc_dt = dt - timedelta(hours=5, minutes=30)
        
        # Calculate Julian Day
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                        utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

        # 3. Set Ayanamsa
        swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_name])

        # 4. Calculate Planets
        results = []
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        
        for p_name, p_id in PLANETS.items():
            res = swe.calc_ut(jd, p_id, flags)
            lon_degree = res[0][0]
            rashi, deg_format = get_rashi_and_degree(lon_degree)
            results.append({"Planet": p_name, "Rashi": rashi, "Degree": deg_format})

        # Calculate Ketu (Always 180 degrees from Rahu)
        rahu_lon = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0][0]
        ketu_lon = (rahu_lon + 180) % 360
        r_k, d_k = get_rashi_and_degree(ketu_lon)
        results.append({"Planet": "Ketu", "Rashi": r_k, "Degree": d_k})

        # 5. Calculate Lagna (Ascendant)
        # 'W' flag is for Whole Sign houses, common in Indian Vedic
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags)
        lagna_lon = ascmc[0]
        l_r, l_d = get_rashi_and_degree(lagna_lon)
        results.insert(0, {"Planet": "Lagna (Asc)", "Rashi": l_r, "Degree": l_d})

        # --- Display Results ---
        st.balloons()
        df = pd.DataFrame(results)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🪐 Planetary Positions")
            st.table(df)
            
        with col2:
            st.subheader("📝 Chart Analysis")
            st.write(f"**Name:** {name}")
            st.write(f"**Ayanamsa:** {ayanamsa_name}")
            st.write(f"**LMT:** {dt.strftime('%d-%m-%Y %H:%M')}")
            st.info("Tip: You can change the Ayanamsa in the sidebar to see how the degrees shift immediately!")

    except Exception as e:
        st.error(f"Error in calculation: {e}")
