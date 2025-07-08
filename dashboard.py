import streamlit as st
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from skyfield.api import load, Topos
from datetime import datetime, timedelta

# 1. User input
st.title("Tonight’s Constellations – Simple Dashboard")
location_input = st.text_input("Enter your location (city, country)", "Tel Aviv")
date_input = st.date_input("Choose a date", datetime.now().date())

# 2. Geocode location
geolocator = Nominatim(user_agent="constellation-dashboard")
location = geolocator.geocode(location_input)
if not location:
    st.error("Location not found!")
    st.stop()

lat, lon = location.latitude, location.longitude

# 3. Prepare time grid
ts = load.timescale()
now = datetime.combine(date_input, datetime.now().time())
times = [now + timedelta(minutes=30*i) for i in range(48)]
sky_times = ts.utc([t.year for t in times], [t.month for t in times], [t.day for t in times],
                   [t.hour for t in times], [t.minute for t in times])

# 4. Sample: some major constellations with main star (can expand!)
CONSTELLATIONS = [
    {'name': 'Orion', 'star': 'Betelgeuse', 'ra_hours': 5 + 55/60, 'dec_deg': 7 + 24/60},
    {'name': 'Ursa Major', 'star': 'Dubhe', 'ra_hours': 11 + 3/60, 'dec_deg': 61 + 45/60},
    {'name': 'Cassiopeia', 'star': 'Schedar', 'ra_hours': 0 + 40/60, 'dec_deg': 56 + 32/60},
    {'name': 'Scorpius', 'star': 'Antares', 'ra_hours': 16 + 29/60, 'dec_deg': -26 - 26/60},
    # ... add more!
]

# 5. Altitude calculations
from skyfield.positionlib import position_of_radec

observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
eph = load('de421.bsp')
results = []
for constellation in CONSTELLATIONS:
    # main star as proxy for constellation
    ra = constellation['ra_hours'] * 15  # to degrees
    dec = constellation['dec_deg']
    altitudes = []
    star = Star(ra_hours=ra/15, dec_degrees=dec)
    for t in sky_times:
        app = eph['earth'] + observer
        alt, az, dist = app.at(t).observe(star).apparent().altaz()
        altitudes.append(alt.degrees)
    altitudes = np.array(altitudes)
    max_idx = np.argmax(altitudes)
    best_time = times[max_idx].strftime('%H:%M')
    is_visible = altitudes[0] > 0
    results.append({
        'Constellation': constellation['name'],
        'Best Hour': best_time,
        'Altitude Now (°)': round(altitudes[0],1),
        'Visible Now': 'Yes' if altitudes[0] > 0 else 'No',
        'Altitudes': altitudes,
        'Times': times
    })

df = pd.DataFrame(results)

# 6. Table display
st.subheader(f"Constellations for {location.address} ({lat:.2f}, {lon:.2f})")
st.dataframe(df[['Constellation','Best Hour','Altitude Now (°)','Visible Now']])

# 7. Interactive plot
selected = st.selectbox("Show altitude curve for:", df['Constellation'])
const_data = df[df['Constellation'] == selected].iloc[0]
altitudes = const_data['Altitudes']
plot_times = [t.strftime('%H:%M') for t in const_data['Times']]

st.line_chart(pd.DataFrame({'Altitude (°)': altitudes}, index=plot_times))

# 8. Placeholder: Moon phase & light pollution
st.info("Moon phase and local light pollution: [Coming soon!]")

st.caption("MVP by Data Science Dashboard Demo")
