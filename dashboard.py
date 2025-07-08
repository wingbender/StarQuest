import streamlit as st
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from skyfield.api import load, Topos
from skyfield.starlib import Star
from datetime import datetime, timedelta

def find_rise_set(times, altitudes):
    above = altitudes > 0
    diff = np.diff(above.astype(int))
    rise_idx = np.where(diff == 1)[0]
    set_idx = np.where(diff == -1)[0]
    if len(rise_idx) == 0 and np.all(above):
        return "Always up", "Always up"
    if len(rise_idx) == 0:
        return "Never up", "Never up"
    rise_time = times[rise_idx[0]+1].strftime('%H:%M')
    set_time = times[set_idx[0]+1].strftime('%H:%M') if len(set_idx) else "-"
    return rise_time, set_time

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
    {'name': 'Andromeda', 'he_name': 'אנדרומדה', 'ra_hours': 1.0, 'dec_deg': 40.0},
    {'name': 'Antlia', 'he_name': 'משאבה', 'ra_hours': 10.25, 'dec_deg': -34.0},
    {'name': 'Apus', 'he_name': 'ציפור גן עדן', 'ra_hours': 16.0, 'dec_deg': -75.0},
    {'name': 'Aquarius', 'he_name': 'דלי', 'ra_hours': 22.5, 'dec_deg': -10.0},
    {'name': 'Aquila', 'he_name': 'נשר', 'ra_hours': 19.75, 'dec_deg': 5.0},
    {'name': 'Ara', 'he_name': 'מזבח', 'ra_hours': 17.5, 'dec_deg': -55.0},
    {'name': 'Aries', 'he_name': 'טלה', 'ra_hours': 2.5, 'dec_deg': 20.0},
    {'name': 'Auriga', 'he_name': 'רכב', 'ra_hours': 5.75, 'dec_deg': 42.0},
    {'name': 'Bootes', 'he_name': 'רועה דובים', 'ra_hours': 15.0, 'dec_deg': 40.0},
    {'name': 'Caelum', 'he_name': 'מפסלת', 'ra_hours': 5.25, 'dec_deg': -42.0},
    {'name': 'Camelopardalis', 'he_name': 'גירפה', 'ra_hours': 7.0, 'dec_deg': 70.0},
    {'name': 'Cancer', 'he_name': 'סרטן', 'ra_hours': 9.0, 'dec_deg': 22.5},
    {'name': 'Canes Venatici', 'he_name': 'כלבי ציד', 'ra_hours': 13.0, 'dec_deg': 40.0},
    {'name': 'Canis Major', 'he_name': 'כלב גדול', 'ra_hours': 7.0, 'dec_deg': -25.0},
    {'name': 'Canis Minor', 'he_name': 'כלב קטן', 'ra_hours': 7.75, 'dec_deg': 5.0},
    {'name': 'Capricornus', 'he_name': 'גדי', 'ra_hours': 21.0, 'dec_deg': -20.0},
    {'name': 'Carina', 'he_name': 'חרטום', 'ra_hours': 9.0, 'dec_deg': -60.0},
    {'name': 'Cassiopeia', 'he_name': 'קסיופאה', 'ra_hours': 1.0, 'dec_deg': 60.0},
    {'name': 'Centaurus', 'he_name': 'קנטאור', 'ra_hours': 13.0, 'dec_deg': -50.0},
    {'name': 'Cepheus', 'he_name': 'ספאוס', 'ra_hours': 22.0, 'dec_deg': 70.0},
    {'name': 'Cetus', 'he_name': 'לוויתן', 'ra_hours': 2.0, 'dec_deg': -10.0},
    {'name': 'Chamaeleon', 'he_name': 'זיקית', 'ra_hours': 10.5, 'dec_deg': -80.0},
    {'name': 'Circinus', 'he_name': 'מחוגה', 'ra_hours': 15.0, 'dec_deg': -65.0},
    {'name': 'Columba', 'he_name': 'יונה', 'ra_hours': 5.5, 'dec_deg': -35.0},
    {'name': 'Coma Berenices', 'he_name': 'שער ברניקי', 'ra_hours': 13.0, 'dec_deg': 25.0},
    {'name': 'Corona Australis', 'he_name': 'כתר דרומי', 'ra_hours': 18.25, 'dec_deg': -40.0},
    {'name': 'Corona Borealis', 'he_name': 'כתר צפוני', 'ra_hours': 16.25, 'dec_deg': 35.0},
    {'name': 'Corvus', 'he_name': 'עורב', 'ra_hours': 12.5, 'dec_deg': -20.0},
    {'name': 'Crater', 'he_name': 'גביע', 'ra_hours': 11.0, 'dec_deg': -15.0},
    {'name': 'Crux', 'he_name': 'צלב דרומי', 'ra_hours': 12.5, 'dec_deg': -60.0},
    {'name': 'Cygnus', 'he_name': 'ברבור', 'ra_hours': 20.5, 'dec_deg': 40.0},
    {'name': 'Delphinus', 'he_name': 'דולפין', 'ra_hours': 20.5, 'dec_deg': 13.0},
    {'name': 'Dorado', 'he_name': 'דג חרב', 'ra_hours': 5.5, 'dec_deg': -65.0},
    {'name': 'Draco', 'he_name': 'דרקון', 'ra_hours': 17.5, 'dec_deg': 65.0},
    {'name': 'Equuleus', 'he_name': 'סוסון', 'ra_hours': 21.25, 'dec_deg': 7.0},
    {'name': 'Eridanus', 'he_name': 'נהר', 'ra_hours': 4.5, 'dec_deg': -20.0},
    {'name': 'Fornax', 'he_name': 'כבשן', 'ra_hours': 3.0, 'dec_deg': -30.0},
    {'name': 'Gemini', 'he_name': 'תאומים', 'ra_hours': 7.0, 'dec_deg': 25.0},
    {'name': 'Grus', 'he_name': 'עגור', 'ra_hours': 22.5, 'dec_deg': -45.0},
    {'name': 'Hercules', 'he_name': 'הרקולס', 'ra_hours': 17.0, 'dec_deg': 30.0},
    {'name': 'Horologium', 'he_name': 'שעון', 'ra_hours': 3.0, 'dec_deg': -55.0},
    {'name': 'Hydra', 'he_name': 'הידרה', 'ra_hours': 10.5, 'dec_deg': -15.0},
    {'name': 'Hydrus', 'he_name': 'נחש מים', 'ra_hours': 2.5, 'dec_deg': -75.0},
    {'name': 'Indus', 'he_name': 'אינדיאני', 'ra_hours': 21.0, 'dec_deg': -55.0},
    {'name': 'Lacerta', 'he_name': 'לטאה', 'ra_hours': 22.5, 'dec_deg': 45.0},
    {'name': 'Leo', 'he_name': 'אריה', 'ra_hours': 11.5, 'dec_deg': 15.0},
    {'name': 'Leo Minor', 'he_name': 'אריה קטן', 'ra_hours': 10.0, 'dec_deg': 35.0},
    {'name': 'Lepus', 'he_name': 'ארנב', 'ra_hours': 5.5, 'dec_deg': -20.0},
    {'name': 'Libra', 'he_name': 'מאזניים', 'ra_hours': 15.5, 'dec_deg': -15.0},
    {'name': 'Lupus', 'he_name': 'זאב', 'ra_hours': 15.0, 'dec_deg': -45.0},
    {'name': 'Lynx', 'he_name': 'שונר', 'ra_hours': 8.0, 'dec_deg': 45.0},
    {'name': 'Lyra', 'he_name': 'נבל', 'ra_hours': 18.5, 'dec_deg': 37.0},
    {'name': 'Mensa', 'he_name': 'שולחן', 'ra_hours': 6.0, 'dec_deg': -80.0},
    {'name': 'Microscopium', 'he_name': 'מיקרוסקופ', 'ra_hours': 21.0, 'dec_deg': -35.0},
    {'name': 'Monoceros', 'he_name': 'קרן חד קרן', 'ra_hours': 7.0, 'dec_deg': -5.0},
    {'name': 'Musca', 'he_name': 'זבוב', 'ra_hours': 12.5, 'dec_deg': -70.0},
    {'name': 'Norma', 'he_name': 'סרגל', 'ra_hours': 16.0, 'dec_deg': -52.0},
    {'name': 'Octans', 'he_name': 'מתומן', 'ra_hours': 22.0, 'dec_deg': -80.0},
    {'name': 'Ophiuchus', 'he_name': 'נושא הנחש', 'ra_hours': 17.5, 'dec_deg': -10.0},
    {'name': 'Orion', 'he_name': 'אוריון', 'ra_hours': 5.5, 'dec_deg': 0.0},
    {'name': 'Pavo', 'he_name': 'טווס', 'ra_hours': 20.0, 'dec_deg': -65.0},
    {'name': 'Pegasus', 'he_name': 'פגסוס', 'ra_hours': 22.0, 'dec_deg': 20.0},
    {'name': 'Perseus', 'he_name': 'פרסאוס', 'ra_hours': 3.5, 'dec_deg': 45.0},
    {'name': 'Phoenix', 'he_name': 'עוף החול', 'ra_hours': 1.0, 'dec_deg': -50.0},
    {'name': 'Pictor', 'he_name': 'צייר', 'ra_hours': 5.5, 'dec_deg': -55.0},
    {'name': 'Pisces', 'he_name': 'דגים', 'ra_hours': 1.0, 'dec_deg': 10.0},
    {'name': 'Piscis Austrinus', 'he_name': 'דג דרומי', 'ra_hours': 22.0, 'dec_deg': -30.0},
    {'name': 'Puppis', 'he_name': 'ירכתיים', 'ra_hours': 7.5, 'dec_deg': -35.0},
    {'name': 'Pyxis', 'he_name': 'מצפן', 'ra_hours': 9.0, 'dec_deg': -30.0},
    {'name': 'Reticulum', 'he_name': 'רשתית', 'ra_hours': 4.0, 'dec_deg': -60.0},
    {'name': 'Sagitta', 'he_name': 'חץ', 'ra_hours': 19.5, 'dec_deg': 18.0},
    {'name': 'Sagittarius', 'he_name': 'קשת', 'ra_hours': 19.0, 'dec_deg': -25.0},
    {'name': 'Scorpius', 'he_name': 'עקרב', 'ra_hours': 17.0, 'dec_deg': -40.0},
    {'name': 'Sculptor', 'he_name': 'פסל', 'ra_hours': 1.0, 'dec_deg': -35.0},
    {'name': 'Scutum', 'he_name': 'מגן', 'ra_hours': 18.75, 'dec_deg': -10.0},
    {'name': 'Serpens', 'he_name': 'נחש', 'ra_hours': 16.5, 'dec_deg': 0.0},
    {'name': 'Sextans', 'he_name': 'ששת', 'ra_hours': 10.25, 'dec_deg': 0.0},
    {'name': 'Taurus', 'he_name': 'שור', 'ra_hours': 4.5, 'dec_deg': 15.0},
    {'name': 'Telescopium', 'he_name': 'טלסקופ', 'ra_hours': 19.25, 'dec_deg': -52.0},
    {'name': 'Triangulum', 'he_name': 'משולש', 'ra_hours': 2.25, 'dec_deg': 32.0},
    {'name': 'Triangulum Australe', 'he_name': 'משולש דרומי', 'ra_hours': 16.0, 'dec_deg': -65.0},
    {'name': 'Tucana', 'he_name': 'טוקן', 'ra_hours': 23.0, 'dec_deg': -70.0},
    {'name': 'Ursa Major', 'he_name': 'דובה גדולה', 'ra_hours': 11.0, 'dec_deg': 55.0},
    {'name': 'Ursa Minor', 'he_name': 'דובה קטנה', 'ra_hours': 15.0, 'dec_deg': 75.0},
    {'name': 'Vela', 'he_name': 'מפרש', 'ra_hours': 9.5, 'dec_deg': -45.0},
    {'name': 'Virgo', 'he_name': 'בתולה', 'ra_hours': 13.5, 'dec_deg': 0.0},
    {'name': 'Volans', 'he_name': 'דג מעופף', 'ra_hours': 8.5, 'dec_deg': -70.0},
    {'name': 'Vulpecula', 'he_name': 'שועל קטן', 'ra_hours': 20.5, 'dec_deg': 25.0},
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
    rise, set_ = find_rise_set(times, altitudes)
    max_idx = np.argmax(altitudes)
    best_time = times[max_idx].strftime('%H:%M')
    is_visible = altitudes[0] > 0
    results.append({
        'Constellation': constellation['name'],
        'שם בעברית': constellation['he_name'],
        'Best Hour': best_time,
        'Rise': rise,
        'Set': set_,
        'Altitude Now (°)': round(altitudes[0],1),
        'Visible Now': 'Yes' if altitudes[0] > 0 else 'No',
        'Altitudes': altitudes,
        'Times': times
    })

df = pd.DataFrame(results)

# 6. Table display
st.subheader(f"Constellations for {location.address} ({lat:.2f}, {lon:.2f})")
st.dataframe(df[['Constellation', 'שם בעברית', 'Best Hour', 'Rise', 'Set', 'Altitude Now (°)', 'Visible Now']])

# 7. Interactive plot
selected = st.selectbox("Show altitude curve for:", df['Constellation'])
const_data = df[df['Constellation'] == selected].iloc[0]
altitudes = const_data['Altitudes']
plot_times = [t.strftime('%H:%M') for t in const_data['Times']]

st.line_chart(pd.DataFrame({'Altitude (°)': altitudes}, index=plot_times))

# 8. Placeholder: Moon phase & light pollution
st.info("Moon phase and local light pollution: [Coming soon!]")

st.caption("MVP by Data Science Dashboard Demo")
