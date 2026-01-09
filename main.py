import os
import streamlit as st
from supabase import create_client, Client
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
import pytz

import altair as alt


import json
import requests
from streamlit_lottie import st_lottie

# import locale

# locale.setlocale(locale.LC_TIME, "el_GR")  # Greek
tz = pytz.timezone('Europe/Athens')

st.set_page_config(
    page_title="Μετεωρολογικά δεδομένα - Δράμα",
    page_icon=":sunny:",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Report a bug': "mailto:kleanthis.xenitidis@gmail.com",
        'About': "# Μετεωρολογικός Σταθμός. *Raspberry Pi!* --- Kleanthis Xenitidis"
    }
)


def m_s_to_bf(ms):
    if 0 <= ms < 0.3:
        return 0
    elif 0.3 <= ms < 1.6:
        return 1
    elif 1.6 <= ms < 3.4:
        return 2
    elif 3.4 <= ms < 5.5:
        return 3
    elif 5.5 <= ms < 8.0:
        return 4
    elif 8.0 <= ms < 10.8:
        return 5
    elif 10.8 <= ms < 13.9:
        return 6
    elif 13.9 <= ms < 17.2:
        return 7
    elif 17.2 <= ms < 20.8:
        return 8
    elif 20.8 <= ms < 24.5:
        return 9
    elif 24.5 <= ms < 28.5:
        return 10
    elif 28.5 <= ms < 32.7:
        return 11
    elif ms > 32.7:
        return 12
    else:
        return None


def bf_string(ms):
    all_strings = [
        "Άπνοια",
        "Σχεδόν άπνοια",
        "Πολύ ασθενής",
        "Ασθενής",
        "Σχεδόν μέτριος",
        "Μέτριος",
        "Ισχυρός",
        "Σφοδρός / Σχεδόν Θυελλώδης",
        "Θυελλώδης",
        "Πολύ Θυελλώδης",
        "Θύελλα",
        "Βίαιη / Σφοδρή θύελλα",
        "Τυφώνας"
    ]
    try:
        result = m_s_to_bf(ms)
        return all_strings[result]
    except:
        return None
    # if 0 <= ms < 0.3:
    #     return "Άπνοια"
    # elif 0.3 <= ms < 1.6:
    #     return "Σχεδόν άπνοια"
    # elif 1.6 <= ms < 3.4:
    #     return "Πολύ ασθενής"
    # elif 3.4 <= ms < 5.5:
    #     return "Ασθενής"
    # elif 5.5 <= ms < 8.0:
    #     return "Σχεδόν μέτριος"
    # elif 8.0 <= ms < 10.8:
    #     return "Μέτριος"
    # elif 10.8 <= ms < 13.9:
    #     return "Ισχυρός"
    # elif 13.9 <= ms < 17.2:
    #     return "Σφοδρός / Σχεδόν Θυελλώδης"
    # elif 17.2 <= ms < 20.8:
    #     return "Θυελλώδης"
    # elif 20.8 <= ms < 24.5:
    #     return "Πολύ Θυελλώδης"
    # elif 24.5 <= ms < 28.5:
    #     return "Θύελλα"
    # elif 28.5 <= ms < 32.7:
    #     return "Βίαιη / Σφοδρή θύελλα"
    # elif ms > 32.7:
    #     return "Τυφώνας"
    # else:
    #     return None


url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

supabase = create_client(url, key)

response = supabase.table('roof_temperature').select("*").execute()
data = response.data

response = supabase.table('roof_humidity').select("*").execute()
data_humidity = response.data

response = supabase.table('roof_pressure').select("*").execute()
data_pressure = response.data

response = supabase.table('roof_wind_speed').select("*").execute()
data_wind_speed = response.data

list_datetimes = list()
list_temperatures = list()

list_h_datetimes = list()
list_humidities = list()

list_p_datetimes = list()
list_pressures = list()

list_ws_datetimes = list()
list_wind_speeds = list()


for i in data:
    t = i["datetime"]
    if '.' in t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
    list_datetimes.append(t.astimezone(tz))

    list_temperatures.append(round(float(i["temperature"]), 1))


for i in data_humidity:
    t = i["datetime"]
    if '.' in t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
    list_h_datetimes.append(t.astimezone(tz))

    list_humidities.append(int(i["humidity"]))


for i in data_pressure:
    t = i["datetime"]
    if '.' in t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
    list_p_datetimes.append(t.astimezone(tz))

    list_pressures.append(int(i["pressure"]))


for i in data_wind_speed:
    t = i["datetime"]
    if '.' in t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
    list_ws_datetimes.append(t.astimezone(tz))

    list_wind_speeds.append(round(float(i["wind_speed"]), 1))


last_temp = list_temperatures[-1]
pre_last_temp = list_temperatures[-2]
delta_temps = round(last_temp - pre_last_temp, 1)

last_humidity = list_humidities[-1]

last_pressure = list_pressures[-1]

last_wind_speed = list_wind_speeds[-1]


df = pd.DataFrame(data={
    'Ημερομηνία/ώρα': list_datetimes,
    'Θερμοκρασία': list_temperatures
})
df['Ημερομηνία'] = df['Ημερομηνία/ώρα'].dt.strftime('%d %b %y')
df['Ώρα'] = df['Ημερομηνία/ώρα'].dt.strftime('%H:%M')
df['Μήνας/Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%m/%Y')
df['Μήν/Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%-m/%Y')
df['Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%Y')
df['Ημέρα του μήνα'] = df['Ημερομηνία/ώρα'].dt.strftime('%d')


df_wind_speed = pd.DataFrame(data={
    'Ημερομηνία/ώρα': list_ws_datetimes,
    'Ταχύτητα ανέμου': list_wind_speeds
})
df_wind_speed['Ημερομηνία'] = df_wind_speed['Ημερομηνία/ώρα'].dt.strftime('%d %b %y')
df_wind_speed['Ώρα'] = df_wind_speed['Ημερομηνία/ώρα'].dt.strftime('%H:%M')
df_wind_speed['Μήνας/Έτος'] = df_wind_speed['Ημερομηνία/ώρα'].dt.strftime('%m/%Y')
df_wind_speed['Μήν/Έτος'] = df_wind_speed['Ημερομηνία/ώρα'].dt.strftime('%-m/%Y')
df_wind_speed['Έτος'] = df_wind_speed['Ημερομηνία/ώρα'].dt.strftime('%Y')
df_wind_speed['Ημέρα του μήνα'] = df_wind_speed['Ημερομηνία/ώρα'].dt.strftime('%d')


df_pressure = pd.DataFrame(data={
    'Ημερομηνία/ώρα': list_p_datetimes,
    'Πίεση': list_pressures
})
df_pressure['Ημερομηνία'] = df_pressure['Ημερομηνία/ώρα'].dt.strftime('%d %b %y')
df_pressure['Ώρα'] = df_pressure['Ημερομηνία/ώρα'].dt.strftime('%H:%M')
df_pressure['Μήνας/Έτος'] = df_pressure['Ημερομηνία/ώρα'].dt.strftime('%m/%Y')
df_pressure['Μήν/Έτος'] = df_pressure['Ημερομηνία/ώρα'].dt.strftime('%-m/%Y')
df_pressure['Έτος'] = df_pressure['Ημερομηνία/ώρα'].dt.strftime('%Y')
df_pressure['Ημέρα του μήνα'] = df_pressure['Ημερομηνία/ώρα'].dt.strftime('%d')


df_humidity = pd.DataFrame(data={
    'Ημερομηνία/ώρα': list_h_datetimes,
    'Υγρασία': list_humidities
})
df_humidity['Ημερομηνία'] = df_humidity['Ημερομηνία/ώρα'].dt.strftime('%d %b %y')
df_humidity['Ώρα'] = df_humidity['Ημερομηνία/ώρα'].dt.strftime('%H:%M')
df_humidity['Μήνας/Έτος'] = df_humidity['Ημερομηνία/ώρα'].dt.strftime('%m/%Y')
df_humidity['Μήν/Έτος'] = df_humidity['Ημερομηνία/ώρα'].dt.strftime('%-m/%Y')
df_humidity['Έτος'] = df_humidity['Ημερομηνία/ώρα'].dt.strftime('%Y')
df_humidity['Ημέρα του μήνα'] = df_humidity['Ημερομηνία/ώρα'].dt.strftime('%d')

today_temps = df.loc[df["Ημερομηνία"] == datetime.today().strftime('%d %b %y')]
today_max = today_temps.loc[today_temps["Θερμοκρασία"].idxmax()]
today_min = today_temps.loc[today_temps["Θερμοκρασία"].idxmin()]

yesterday_temps = df.loc[(df["Ημερομηνία"] == (datetime.today() - timedelta(days=1)).strftime('%d %b %y'))
    & (df['Ώρα'] == list_datetimes[-1].strftime('%H:%M'))]
yesterday_same_time = yesterday_temps.iloc[0]["Θερμοκρασία"]


url = requests.get("https://lottie.host/387e15ac-14bf-4416-9a93-2e6481c47788/IB9cC9BNaZ.json")
url_json = dict()
if url.status_code == 200:
    url_json = url.json()
else:
    print("Error in the URL")
st_lottie(url_json,
          reverse=True,
          height=150,
          width=150,
          speed=1,
          loop=True,
          quality='high')

st.subheader(':sunny::cloud::umbrella::snowflake:')

col1, col2 = st.columns(2)
with col1:
    st.write(list_datetimes[-1].strftime("%A, %d/%m/%y **(%H:%M)**"))
    st.metric(label="Θερμοκρασία", value=f'{last_temp} °C', delta=f"{delta_temps} °C")

with col2:
    ttt = today_max["Ημερομηνία/ώρα"].strftime('%H:%M')
    ddd = today_min["Ημερομηνία/ώρα"].strftime('%H:%M')
    f'μέγιστη: :thermometer: **{today_max["Θερμοκρασία"]} °C** :clock1: :red-background[{ttt}]'
    f'ελάχιστη: :thermometer: **{today_min["Θερμοκρασία"]} °C** :clock1: :blue-background[{ddd}]'
    # st.markdown("***")
    f'χθες ίδια ώρα: :thermometer: **{yesterday_same_time} °C**'

'---'
col1, col2, col3 = st.columns(3)
with col1:
    url = requests.get("https://lottie.host/387e15ac-14bf-4416-9a93-2e6481c47788/IB9cC9BNaZ.json")
    url_json = dict()
    if url.status_code == 200:
        url_json = url.json()
    else:
        print("Error in the URL")
    st_lottie(url_json,
              reverse=True,
              height=100,
              width=100,
              speed=1,
              loop=True,
              quality='high')
    st.write(list_ws_datetimes[-1].strftime("%d/%m/%y **(%H:%M)**"))
    st.write(f'Ταχύτητα ανέμου :dash: :green[{last_wind_speed} m/s]')
    with st.expander("Περισσότερα"):
        st.write(f':dash: :green[{round(3.6 * last_wind_speed, 2)} χλμ/ώρα]')
        st.write(f':dash: :green[{m_s_to_bf(last_wind_speed)} Μποφόρ]')
        st.write(f'Χαρακτηρισμός ανέμου: :green[{bf_string(last_wind_speed)}]')
with col2:
    url = requests.get("https://lottie.host/7d8cf8a1-9873-4ad5-9936-a37022d51614/dMQ4AYnYzG.json")
    url_json = dict()
    if url.status_code == 200:
        url_json = url.json()
    else:
        print("Error in the URL")
    st_lottie(url_json,
              reverse=True,
              height=100,
              width=100,
              speed=1,
              loop=True,
              quality='high')
    st.write(list_h_datetimes[-1].strftime("%d/%m/%y **(%H:%M)**"))
    st.write(f'Υγρασία :sparkle: :blue[{last_humidity}] :blue[%]')
with col3:
    url = requests.get("https://lottie.host/387e15ac-14bf-4416-9a93-2e6481c47788/IB9cC9BNaZ.json")
    url_json = dict()
    if url.status_code == 200:
        url_json = url.json()
    else:
        print("Error in the URL")
    st_lottie(url_json,
              reverse=True,
              height=100,
              width=100,
              speed=1,
              loop=True,
              quality='high')
    st.write(list_p_datetimes[-1].strftime("%d/%m/%y **(%H:%M)**"))
    st.write(f'Ατμ. πίεση :large_purple_circle: :red[{last_pressure/100} hPa]')

'---'

# Λογική πρόγνωσης

def analyze_weather(temps, press, winds, hums):
    # Έλεγχος αν έχουμε αρκετά δεδομένα (τουλάχιστον 3 ωρών = 6 μετρήσεις)
    if len(press) < 6:
        return "Not enough data", "gray"

    # --- Τελευταίες Τιμές ---
    curr_p = press[-1]
    curr_w = winds[-1]
    curr_h = hums[-1]
    
    # --- Υπολογισμός Τάσης Πίεσης (Τελευταίες 3 ώρες = 6 μετρήσεις πίσω) ---
    # Συγκρίνουμε το τώρα με 3 ώρες πριν για να αποφύγουμε τον θόρυβο των 0.3 μονάδων
    p_3h_ago = press[-6]
    p_trend = curr_p - p_3h_ago 
    
    # --- LOGIC RULES ---
    
    # ΚΑΝΟΝΑΣ 1: Ισχυρός Άνεμος (με βάση τον 'αναίσθητο' αισθητήρα σου)
    if curr_w >= 3:
        return f"⚠️ ΠΡΟΣΟΧΗ: Πολύ ισχυροί άνεμοι! (Ενδειξη: {curr_w}/4)", "error"

    # ΚΑΝΟΝΑΣ 2: Καταιγίδα (Πίεση πέφτει γρήγορα + Υγρασία ψηλά)
    # Αν η πίεση έπεσε πάνω από 2 μονάδες σε 3 ώρες
    if p_trend < -2.0:
        if curr_h > 80:
             return "⛈️ ΕΡΧΕΤΑΙ ΚΑΤΑΙΓΙΔΑ: Ραγδαία πτώση πίεσης & υψηλή υγρασία.", "error"
        else:
             return "💨 ΕΡΧΕΤΑΙ ΚΑΚΟΚΑΙΡΙΑ/ΑΕΡΑΣ: Ραγδαία πτώση πίεσης.", "warning"

    # ΚΑΝΟΝΑΣ 3: Πιθανή Βροχή (Αργή πτώση πίεσης)
    elif p_trend < -0.5: # Αγνοούμε πτώση μικρότερη του 0.5 λόγω θορύβου
        if curr_h > 85:
            return "🌧️ ΠΙΘΑΝΗ ΒΡΟΧΗ: Η πίεση πέφτει σταθερά, η ατμόσφαιρα είναι υγρή.", "warning"
        else:
            return "☁️ ΣΥΝNEΦΙΑ/ΑΣΤΑΘΕΙΑ: Η πίεση πέφτει αργά.", "info"

    # ΚΑΝΟΝΑΣ 4: Βελτίωση (Άνοδος πίεσης)
    elif p_trend > 0.5:
        if curr_w >= 2:
             return "🌬️ ΚΑΘΑΡΙΖΕΙ Ο ΚΑΙΡΟΣ (αλλά με αέρα): Η πίεση ανεβαίνει.", "success"
        else:
             return "☀️ ΚΑΛΟΣ ΚΑΙΡΟΣ: Η πίεση ανεβαίνει ή είναι σταθερά υψηλή.", "success"

    # ΚΑΝΟΝΑΣ 5: Στασιμότητα (Ο θόρυβος που ανέφερες +/- 0.3 εμπίπτει εδώ)
    else:
        return "⚖️ ΣΤΑΘΕΡΟΣ ΚΑΙΡΟΣ: Καμία σημαντική μεταβολή.", "success"



# καρτέλα πρόγνωσης

st.title("🌤️ Local Weather Nowcasting")
st.caption("Πρόβλεψη βάσει τοπικών μετρήσεων (χωρίς Internet)")

# Κλήση της συνάρτησης πρόβλεψης
forecast_msg, status_color = analyze_weather(list_temperatures, list_pressures, list_wind_speeds, list_humidities)

# Εμφάνιση Πρόβλεψης σε πλαίσιο
st.subheader("🔮 Πρόγνωση Επόμενων Ωρών")
if status_color == "error":
    st.error(forecast_msg)
elif status_color == "warning":
    st.warning(forecast_msg)
elif status_color == "success":
    st.success(forecast_msg)
else:
    st.info(forecast_msg)

# Εμφάνιση Τρεχουσών Μετρήσεων (Metrics)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Θερμοκρασία", f"{list_temperatures[-1]:.1f} °C", delta=f"{list_temperatures[-1]-list_temperatures[-2]:.1f}")
col2.metric("Πίεση", f"{list_pressures[-1]:.1f} hPa", delta=f"{list_pressures[-1]-list_pressures[-6]:.1f} (3h)")
col3.metric("Υγρασία", f"{list_humidities[-1]} %")
col4.metric("Άνεμος (0-4)", f"{list_wind_speeds[-1]}", help="Κλίμακα έντασης: 3-4 = Πολύ Ισχυρός")

st.divider()

# Γραφήματα
st.subheader("📊 Τάσεις (Τελευταίο 24ωρο)")

# Φτιάχνουμε DataFrame για εύκολο plotting
df_ai = pd.DataFrame({
    'Θερμοκρασία': list_temperatures[-48:],
    'Πίεση': list_pressures[-48:],
    'Υγρασία': list_humidities[-48:],
    'Άνεμος': list_wind_speeds[-48:]
})

# Γράφημα Πίεσης (Το πιο σημαντικό)
st.write("**Βαρομετρική Πίεση** (Κλειδί για πρόγνωση)")
st.line_chart(df_ai['Πίεση'])

# Γράφημα Ανέμου & Υγρασίας
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.write("**Ένταση Ανέμου**")
    st.bar_chart(df_ai['Άνεμος']) # Bar chart γιατί οι τιμές είναι διακριτές (0,1,2,3,4)
with col_g2:
    st.write("**Υγρασία**")
    st.line_chart(df_ai['Υγρασία'])


#######################


tab_day, tab_month, tab_year = st.tabs(["Ημερησίως", "Μηνιαία", "Ετήσια"])

with tab_day:
    td = datetime.today()
    st.write("**Σήμερα:** ", td.strftime("%A"), f'{td.day}/{td.month}/{td.year}')
    day = st.date_input(":date: Επιλογή ημέρας"
                        , value="today"
                        , format="DD/MM/YYYY"
                        )
    next_day = day + timedelta(days=1)
    st.write("**Επιλεγμένη ημερομηνία:** ", f'{day.day}/{day.month}/{day.year}')
    filtered_df = df.loc[(df["Ημερομηνία/ώρα"] >= day.strftime('%Y-%m/%d')) & (df["Ημερομηνία/ώρα"] <=
                                                                               next_day.strftime('%Y-%m/%d'))]
    filtered_df_wind_speed = df_wind_speed.loc[(df_wind_speed["Ημερομηνία/ώρα"] >= day.strftime('%Y-%m/%d')) &
                                           (df_wind_speed["Ημερομηνία/ώρα"] <= next_day.strftime('%Y-%m/%d'))]
    filtered_df_pressure = df_pressure.loc[(df_pressure["Ημερομηνία/ώρα"] >= day.strftime('%Y-%m/%d')) &
                                           (df_pressure["Ημερομηνία/ώρα"] <= next_day.strftime('%Y-%m/%d'))]
    filtered_df_humidity = df_humidity.loc[(df_humidity["Ημερομηνία/ώρα"] >= day.strftime('%Y-%m/%d')) &
                                           (df_humidity["Ημερομηνία/ώρα"] <= next_day.strftime('%Y-%m/%d'))]
    if filtered_df.size > 0:
        c1, c2, c3 = st.columns(3)
        with c1:
            # filtered_df_max = filtered_df.loc[today_temps["Θερμοκρασία"].idxmax()]
            filtered_df_max = filtered_df[filtered_df["Θερμοκρασία"] == filtered_df["Θερμοκρασία"].max()]
            st.write(f'**Μέγιστη:** {filtered_df_max.iloc[0]["Θερμοκρασία"]} °C')
            for i in range(filtered_df_max["Θερμοκρασία"].count()):
                st.write(f':clock1: {filtered_df_max.iloc[i]["Ώρα"]}')
        with c2:
            # filtered_df_max = filtered_df.loc[today_temps["Θερμοκρασία"].idxmax()]
            filtered_df_min = filtered_df[filtered_df["Θερμοκρασία"] == filtered_df["Θερμοκρασία"].min()]
            st.write(f'**Ελάχιστη:** {filtered_df_min.iloc[0]["Θερμοκρασία"]} °C')
            for i in range(filtered_df_min["Θερμοκρασία"].count()):
                st.write(f':clock1: {filtered_df_min.iloc[i]["Ώρα"]}')
        with c3:
            st.write(f'**Μέση:** {round(filtered_df["Θερμοκρασία"].mean(), 1)} °C')
        st.line_chart(filtered_df, y="Θερμοκρασία", x='Ώρα')

    if filtered_df_wind_speed.size > 0:
        st.line_chart(filtered_df_wind_speed, y="Ταχύτητα ανέμου", x='Ώρα')

    if filtered_df_pressure.size > 0:
        min_val = filtered_df_pressure.loc[filtered_df_pressure["Πίεση"].idxmin()]["Πίεση"]
        max_val = filtered_df_pressure.loc[filtered_df_pressure["Πίεση"].idxmax()]["Πίεση"]
        c = (
            alt.Chart(filtered_df_pressure)
            .mark_line()
            .encode(alt.Y('Πίεση').scale(domain=(min_val, max_val)), x="Ώρα")
        )

        st.altair_chart(c, use_container_width=True)
        # st.line_chart(filtered_df_pressure, y="Πίεση", x='Ώρα')

    if filtered_df_humidity.size > 0:
        st.line_chart(filtered_df_humidity, y="Υγρασία", x='Ώρα')

    if filtered_df.size > 0:
        st.dataframe(filtered_df
                    .style.highlight_max(axis=0, subset=['Θερμοκρασία'], props='background-color:red;')
                    .highlight_min(axis=0, subset=['Θερμοκρασία'], props='background-color:blue;')
                     .format(precision=1),
                    column_order=["Ώρα", "Θερμοκρασία"],
                    hide_index=True,
                    use_container_width=True)
    else:
        st.write("Δεν υπάρχουν δεδομένα θερμοκρασίας για αυτήν την ημερμηνία.")
    if filtered_df_wind_speed.size > 0:
        st.dataframe(filtered_df_wind_speed
                    .style.highlight_max(axis=0, subset=['Ταχύτητα ανέμου'], props='background-color:red;')
                     .format(precision=1),
                    column_order=["Ώρα", "Ταχύτητα ανέμου"],
                    hide_index=True,
                    use_container_width=True)
    else:
        st.write("Δεν υπάρχουν δεδομένα ταχύτητας ανέμου για αυτήν την ημερμηνία.")
    if filtered_df_pressure.size > 0:
        st.dataframe(filtered_df_pressure
                    .style.highlight_max(axis=0, subset=['Πίεση'], props='background-color:red;')
                    .highlight_min(axis=0, subset=['Πίεση'], props='background-color:blue;')
                     .format(precision=1),
                    column_order=["Ώρα", "Πίεση"],
                    hide_index=True,
                    use_container_width=True)
    else:
        st.write("Δεν υπάρχουν δεδομένα ατμ. πίεσης για αυτήν την ημερμηνία.")
    if filtered_df_humidity.size > 0:
        st.dataframe(filtered_df_humidity
                    .style.highlight_max(axis=0, subset=['Υγρασία'], props='background-color:red;')
                    .highlight_min(axis=0, subset=['Υγρασία'], props='background-color:blue;')
                     .format(precision=1),
                    column_order=["Ώρα", "Υγρασία"],
                    hide_index=True,
                    use_container_width=True)
    else:
        st.write("Δεν υπάρχουν δεδομένα υγρασίας για αυτήν την ημερμηνία.")


def go_to_next_month():
    if st.session_state['month'] < 12:
        st.session_state['month'] = int(st.session_state['month']) + 1
    else:
        st.session_state['month'] = 1
        st.session_state['year'] = int(st.session_state['year']) + 1


def go_to_previous_month():
    if st.session_state['month'] > 1:
        st.session_state['month'] = int(st.session_state['month']) - 1
    else:
        st.session_state['month'] = 12
        st.session_state['year'] = int(st.session_state['year']) - 1


with tab_month:
    # '''Λίστα με όλες τις ημέρες του μήνα (μέγιστη, ελάχιστη, μέση)'''
    if 'month' in st.session_state and 'year' in st.session_state:
        month = st.session_state['month']
        year = st.session_state['year']
        selected_month = datetime.now().replace(year=year, month=month)
    else:
        selected_month = datetime.now()
        st.session_state['month'] = datetime.now().month
        st.session_state['year'] = datetime.now().year
        month = st.session_state['month']
        year = st.session_state['year']

    filtered_df_month = df.loc[(df["Μήνας/Έτος"] == selected_month.strftime('%m/%Y'))]
    filtered_df_p_month = df_pressure.loc[(df_pressure["Μήνας/Έτος"] == selected_month.strftime('%m/%Y'))]
    filtered_df_h_month = df_humidity.loc[(df_humidity["Μήνας/Έτος"] == selected_month.strftime('%m/%Y'))]
    filtered_df_ws_month = df_wind_speed.loc[(df_wind_speed["Μήνας/Έτος"] == selected_month.strftime('%m/%Y'))]

    c_month_1, c_month_2, c_month_3 = st.columns(3)
    with c_month_2:
        st.subheader(f'{selected_month.strftime("%B")} {selected_month.year}')
    with c_month_1:
        st.button("Προηγούμενος Μήνας", on_click=go_to_previous_month)
    with c_month_3:
        st.button(label="Επόμενος Μήνας", on_click=go_to_next_month)

    # st.line_chart(filtered_df_month, x="Ημέρα του μήνα", y="Θερμοκρασία")
    all_max = list()
    all_min = list()
    all_mean = list()
    for i in pd.unique(filtered_df_month["Ημέρα του μήνα"]):
        # st.write(filtered_df_month)
        # st.write(filtered_df_month["Ημέρα του μήνα"] == f'{i}')
        current_values = filtered_df_month[filtered_df_month["Ημέρα του μήνα"] == f'{i}']
        current_max = current_values["Θερμοκρασία"].max()
        all_max.append(current_max)
        current_min = current_values["Θερμοκρασία"].min()
        all_min.append(current_min)
        current_mean = round(current_values["Θερμοκρασία"].mean(), 1)
        all_mean.append(current_mean)
    min_max_mean = pd.DataFrame(
        data={
            'Ημέρα': pd.unique(filtered_df_month["Ημέρα του μήνα"]),
            'Ελάχιστη': all_min,
            'Μέση': all_mean,
            'Μέγιστη': all_max
        })
    min_max_mean = min_max_mean.sort_values(by=['Ημέρα'])
    st.write("Θερμοκρασία")
    chart_data = pd.DataFrame(min_max_mean, columns=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"])
    st.line_chart(chart_data, x="Ημέρα", y=["Ελάχιστη", "Μέση", "Μέγιστη"])

    all_ws_max = list()
    all_ws_min = list()
    all_ws_mean = list()
    for i in pd.unique(filtered_df_ws_month["Ημέρα του μήνα"]):
        # st.write(filtered_df_month)
        # st.write(filtered_df_month["Ημέρα του μήνα"] == f'{i}')
        current_values = filtered_df_ws_month[filtered_df_ws_month["Ημέρα του μήνα"] == f'{i}']
        current_max = current_values["Ταχύτητα ανέμου"].max()
        all_ws_max.append(current_max)
        current_min = current_values["Ταχύτητα ανέμου"].min()
        all_ws_min.append(current_min)
        current_mean = round(current_values["Ταχύτητα ανέμου"].mean(), 1)
        all_ws_mean.append(current_mean)

    if len(all_ws_min) > 0:
        min_max_mean_ws = pd.DataFrame(
            data={
                'Ημέρα': pd.unique(filtered_df_ws_month["Ημέρα του μήνα"]),
                'Ελάχιστη': all_ws_min,
                'Μέση': all_ws_mean,
                'Μέγιστη': all_ws_max
            })
        min_max_mean_ws = min_max_mean_ws.sort_values(by=['Ημέρα'])
        st.write("Ταχύτητα ανέμου")
        chart_data = pd.DataFrame(min_max_mean_ws, columns=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"])
        st.line_chart(chart_data, x="Ημέρα", y=["Ελάχιστη", "Μέση", "Μέγιστη"])

    all_p_max = list()
    all_p_min = list()
    all_p_mean = list()
    for i in pd.unique(filtered_df_p_month["Ημέρα του μήνα"]):
        # st.write(filtered_df_month)
        # st.write(filtered_df_month["Ημέρα του μήνα"] == f'{i}')
        current_values = filtered_df_p_month[filtered_df_p_month["Ημέρα του μήνα"] == f'{i}']
        current_max = current_values["Πίεση"].max()
        all_p_max.append(current_max)
        current_min = current_values["Πίεση"].min()
        all_p_min.append(current_min)
        current_mean = round(current_values["Πίεση"].mean(), 1)
        all_p_mean.append(current_mean)

    if len(all_p_min) > 0:
        min_max_mean_p = pd.DataFrame(
            data={
                'Ημέρα': pd.unique(filtered_df_p_month["Ημέρα του μήνα"]),
                'Ελάχιστη': all_p_min,
                'Μέση': all_p_mean,
                'Μέγιστη': all_p_max
            })
        min_max_mean_p = min_max_mean_p.sort_values(by=['Ημέρα'])
        # chart_data = pd.DataFrame(min_max_mean_p, columns=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"])
        # st.line_chart(chart_data, x="Ημέρα", y=["Ελάχιστη", "Μέση", "Μέγιστη"])

        min_val = min(all_p_min)
        max_val = max(all_p_max)
        c = (
            alt.Chart(min_max_mean_p)
            .mark_line()
            .encode(alt.Y("Ελάχιστη").scale(domain=(min_val, max_val)), x="Ημέρα", color=alt.value("#d61a1f"))
        )
        d = (
            alt.Chart(min_max_mean_p)
            .mark_line()
            .encode(alt.Y("Μέγιστη").scale(domain=(min_val, max_val)), x="Ημέρα", color=alt.value("#5453c6"))
        )
        e = (
            alt.Chart(min_max_mean_p)
            .mark_line()
            .encode(alt.Y("Μέση").scale(domain=(min_val, max_val)), x="Ημέρα", color=alt.value("#f9c31a"))
        )
        st.write("Ατμοσφαιρική Πίεση")
        st.altair_chart(c + d + e, use_container_width=True)

    all_h_max = list()
    all_h_min = list()
    all_h_mean = list()
    for i in pd.unique(filtered_df_h_month["Ημέρα του μήνα"]):
        # st.write(filtered_df_month)
        # st.write(filtered_df_month["Ημέρα του μήνα"] == f'{i}')
        current_values = filtered_df_h_month[filtered_df_h_month["Ημέρα του μήνα"] == f'{i}']
        current_max = current_values["Υγρασία"].max()
        all_h_max.append(current_max)
        current_min = current_values["Υγρασία"].min()
        all_h_min.append(current_min)
        current_mean = round(current_values["Υγρασία"].mean(), 1)
        all_h_mean.append(current_mean)

    if len(all_h_min) > 0:
        min_max_mean_h = pd.DataFrame(
            data={
                'Ημέρα': pd.unique(filtered_df_h_month["Ημέρα του μήνα"]),
                'Ελάχιστη': all_h_min,
                'Μέση': all_h_mean,
                'Μέγιστη': all_h_max
            })
        min_max_mean_h = min_max_mean_h.sort_values(by=['Ημέρα'])
        st.write("Υγρασία")
        chart_data = pd.DataFrame(min_max_mean_h, columns=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"])
        st.line_chart(chart_data, x="Ημέρα", y=["Ελάχιστη", "Μέση", "Μέγιστη"])

    st.subheader(f'{month}/{year} | Θερμοκρασία', divider='rainbow')
    st.dataframe(min_max_mean, column_order=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"], hide_index=True, use_container_width=True)
    if len(all_ws_min) > 0:
        st.subheader(f'{month}/{year} | Ταχύτητα ανέμου', divider='rainbow')
        st.dataframe(min_max_mean_ws, column_order=["Ημέρα", "Μέση", "Μέγιστη"], hide_index=True,
                     use_container_width=True)
    if len(all_p_min) > 0:
        st.subheader(f'{month}/{year} | Ατμοσφαιρική Πίεση', divider='rainbow')
        st.dataframe(min_max_mean_p, column_order=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"], hide_index=True,
                     use_container_width=True)
    if len(all_h_min) > 0:
        st.subheader(f'{month}/{year} | Υγρασία', divider='rainbow')
        st.dataframe(min_max_mean_h, column_order=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"], hide_index=True,
                     use_container_width=True)

with tab_year:
    option = st.selectbox("Επιλογή έτους", pd.unique(df["Έτος"]))
    st.write("Επιλεγμένο έτος: ", option)
    filtered_df_year = df.loc[df["Έτος"] == f'{option}']
    filtered_df_year_ws = df_wind_speed.loc[df_wind_speed["Έτος"] == f'{option}']
    filtered_df_year_p = df_pressure.loc[df_pressure["Έτος"] == f'{option}']
    filtered_df_year_h = df_humidity.loc[df_humidity["Έτος"] == f'{option}']
    for i in range(12):
        filtered_df_year_per_month = df.loc[df["Μήν/Έτος"] == f'{i+1}/{option}']
        if filtered_df_year_per_month.size > 0:
            f':sunny: Μήνας: {i+1}/{option}'
            f':gray[**Μέση** :thermometer: {round(filtered_df_year_per_month["Θερμοκρασία"].mean(), 1)}] | :red[**Μέγιστη** :thermometer: {round(filtered_df_year_per_month["Θερμοκρασία"].max(), 1)}] | :blue[**Ελάχιστη** :thermometer: {round(filtered_df_year_per_month["Θερμοκρασία"].min(), 1)}]'
            '---'
    chart = alt.Chart(filtered_df_year).mark_boxplot(extent='min-max').encode(
        x='Μήν/Έτος',
        y='Θερμοκρασία'
    )
    chart_ws = alt.Chart(filtered_df_year_ws).mark_boxplot(extent='min-max').encode(
        x='Μήν/Έτος',
        y='Ταχύτητα ανέμου'
    )

    min_val = filtered_df_year_p.loc[filtered_df_year_p["Πίεση"].idxmin()]["Πίεση"]
    max_val = filtered_df_year_p.loc[filtered_df_year_p["Πίεση"].idxmax()]["Πίεση"]
    chart_p = alt.Chart(filtered_df_year_p).mark_boxplot(extent='min-max').encode(
        alt.Y("Πίεση").scale(domain=(min_val, max_val)),
        x='Μήν/Έτος'
    )
    chart_h = alt.Chart(filtered_df_year_h).mark_boxplot(extent='min-max').encode(
        x='Μήν/Έτος',
        y='Υγρασία'
    )
    st.subheader(f'{option}', divider='rainbow')
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
    st.altair_chart(chart_ws, theme="streamlit", use_container_width=True)
    st.altair_chart(chart_p, theme="streamlit", use_container_width=True)
    st.altair_chart(chart_h, theme="streamlit", use_container_width=True)

# st.write(data)

'---'

st.image('https://lh3.googleusercontent.com/a/ACg8ocKf_BEQXNtWgvgzj2Jump2CMCB5dCo95RWSdQdsh_67Ga3prkYU=s288-c-no',
         caption='Designed by Kleanthis Xenitidis', width=100)
st.link_button("xenitidis.eu", "https://www.xenitidis.eu")