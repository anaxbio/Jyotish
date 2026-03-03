import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pandas as pd

# --- Configuration ---
st.set_page_config(page_title="Vedic Patrika Pro", layout="wide", page_icon="🕉️")
geolocator = Nominatim(user_agent="vedic_astro_app_v2")

# Ayanamsa IDs (Using Integer IDs for stability)
AYANAMSA_MAP = {
    "Lahiri (Chitra Paksha)": 1,
    "Raman": 3,
    "KP (Krishnamurti)": 5,
    "Pushya Paksha": 41,
    "Fagan-Bradley": 0
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
    "Rahu": swe.MEAN_NODE, 
}

def get_rashi_and_degree(total_degree):
    rashi_idx = int(total_degree / 30) % 12
    degree_in_rashi = total_degree % 30
    minutes = (degree_in_rashi - int(degree_in_rashi)) * 60
    seconds = (minutes - int(minutes)) * 60
    return RASHI_NAMES[rashi_idx], f"{int(degree_in_rashi)}° {int(minutes)}' {int(seconds)}\""

# --- UI Header ---
st.title("🕉️ Vedic Patrika Pro")
st.markdown("---")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("📍 Birth Details")
    name = st.text_input("Person's Name", "New Patrika")
    dob = st.date_input("Date of Birth", value=datetime(1980, 1, 1))
    
    # FIXED: Added step=60 for 1-minute precision
    tob = st.time_input("Time of Birth", value=datetime.strptime("12:00", "%H:%M").time(), step=60)
    
    st.divider()
    
    # CITY LOOKUP
    city_query = st.text_input("Birth City (e.g. Mumbai, India)", "Mumbai")
    timezone_offset = st.number_input("Timezone Offset (IST = 5.5)", value=5.5, step=0.5)
    
    st.divider()
    
    # AYANAMSA
    ayan_choice = st.selectbox("Ayanamsa Method", list(AYANAMSA_MAP.keys()))
    
    st.info("Calculations powered by Swiss Ephemeris.")

# --- CALCULATION LOGIC ---
if st.button("Generate Accurate Patrika"):
    try:
        # 1. Geolocation
        location = geolocator.geocode(city_query)
        if location:
            lat, lon = location.latitude, location.longitude
            st.success(f"Location Found: {location.address[:40]}...")
        else:
            st.warning("City not found. Defaulting to Mumbai (19.07, 72.87)")
            lat, lon = 19.0760, 72.8777

        # 2. Time Conversion to UTC
        # Proper precision: Hours + Minutes/60 + Seconds/3600
        local_dt = datetime.combine(dob, tob)
        utc_dt = local_dt - timedelta(hours=timezone_offset)
        
        # Calculate Julian Day for the engine
        jd_utc = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                            utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

        # 3. Apply Ayanamsa
        swe.set_sid_mode(AYANAMSA_MAP[ayan_choice])

        # 4. Planetary Calculations
        results = []
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        
        # Calculate Lagna (Ascendant) First
        # 'W' is for Whole Sign Houses (Standard for Vedic)
        cusps, ascmc = swe.houses_ex(jd_utc, lat, lon, b'W', flags)
        lagna_lon = ascmc[0]
        l_r, l_d = get_rashi_and_degree(lagna_lon)
        results.append({"Entity": "Lagna (Ascendant)", "Rashi": l_r, "Position": l_d})

        # Calculate Planets
        for p_name, p_id in PLANETS.items():
            res = swe.calc_ut(jd_utc, p_id, flags)
            lon_deg = res[0][0]
            rashi, deg_fmt = get_rashi_and_degree(lon_deg)
            results.append({"Entity": p_name, "Rashi": rashi, "Position": deg_fmt})

        # Ketu (Calculated as 180 degrees from Rahu)
        rahu_lon = swe.calc_ut(jd_utc, swe.MEAN_NODE, flags)[0][0]
        ketu_lon = (rahu_lon + 180) % 360
        k_r, k_d = get_rashi_and_degree(ketu_lon)
        results.append({"Entity": "Ketu", "Rashi": k_r, "Position": k_d})

        # --- DISPLAY OUTPUT ---
        st.balloons()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🪐 Planetary Positions (Sidereal)")
            df = pd.DataFrame(results)
            st.table(df)

        with col2:
            st.subheader("📝 Birth Data Summary")
            st.write(f"**Name:** {name}")
            st.write(f"**Local Time:** {local_dt.strftime('%d-%m-%Y %H:%M')}")
            st.write(f"**Coordinates:** {lat:.2f}N, {lon:.2f}E")
            st.write(f"**Ayanamsa:** {ayan_choice}")
            
            st.info("This chart is calculated using the Whole Sign house system, standard for Vedic Astrology.")

    except Exception as e:
        st.error(f"Error in generation: {e}")
