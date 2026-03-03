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
        p_list = "\n".join(house_data
