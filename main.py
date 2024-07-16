import os
import streamlit as st
from supabase import create_client, Client
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
import pytz

import altair as alt

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
    st.write(list_h_datetimes[-1].strftime("%d/%m/%y **(%H:%M)**"))
    st.write(f'Υγρασία :sparkle: :blue[{last_humidity}] :blue[%]')
with col2:
    st.write(list_ws_datetimes[-1].strftime("%d/%m/%y **(%H:%M)**"))
    st.write(f'Ταχύτητα ανέμου :dash: :green[{last_wind_speed} m/s]')
with col3:
    st.write(list_p_datetimes[-1].strftime("%d/%m/%y **(%H:%M)**"))
    st.write(f'Ατμ. πίεση :large_purple_circle: :red[{last_pressure/100} hPa]')
'---'

# st.write(df)

# st.line_chart(df, y="Θερμοκρασία", x='Ημερομηνία/ώρα')

# st.header("Weather Station")

tab_day, tab_month, tab_year = st.tabs(["Ημερησίως", "Μηνιαία", "Ετήσια"])

with tab_day:
    td = datetime.today()
    st.write("**Σήμερα:** ", td.strftime("%A"), f'{td.day}/{td.month}/{td.year}')
    day = st.date_input(":date: Επιλογή ημέρας"
                        , value="default_value_today"
                        , format="DD/MM/YYYY"
                        )
    next_day = day + timedelta(days=1)
    st.write("**Επιλεγμένη ημερομηνία:** ", f'{day.day}/{day.month}/{day.year}')
    filtered_df = df.loc[(df["Ημερομηνία/ώρα"] >= day.strftime('%Y-%m/%d')) & (df["Ημερομηνία/ώρα"] <=
                                                                               next_day.strftime('%Y-%m/%d'))]
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
    if filtered_df_pressure.size > 0:
        st.dataframe(filtered_df_pressure
                    .style.highlight_max(axis=0, subset=['Πίεση'], props='background-color:red;')
                    .highlight_min(axis=0, subset=['Πίεση'], props='background-color:blue;')
                     .format(precision=1),
                    column_order=["Ώρα", "Πίεση"],
                    hide_index=True,
                    use_container_width=True)
    if filtered_df_humidity.size > 0:
        st.dataframe(filtered_df_humidity
                    .style.highlight_max(axis=0, subset=['Υγρασία'], props='background-color:red;')
                    .highlight_min(axis=0, subset=['Υγρασία'], props='background-color:blue;')
                     .format(precision=1),
                    column_order=["Ώρα", "Υγρασία"],
                    hide_index=True,
                    use_container_width=True)
    else:
        st.subheader("Δεν υπάρχουν δεδομένα για αυτήν την ημερμηνία.")


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
    st.altair_chart(chart_p, theme="streamlit", use_container_width=True)
    st.altair_chart(chart_h, theme="streamlit", use_container_width=True)

# st.write(data)

'---'

st.image('https://lh3.googleusercontent.com/a/ACg8ocKf_BEQXNtWgvgzj2Jump2CMCB5dCo95RWSdQdsh_67Ga3prkYU=s288-c-no',
         caption='Designed by Kleanthis Xenitidis', width=100)
st.link_button("xenitidis.eu", "https://www.xenitidis.eu")