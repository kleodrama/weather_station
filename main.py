import os
import streamlit as st
from supabase import create_client, Client
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
import pytz

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

list_datetimes = list()
list_temperatures = list()

# '''TODO: function that converts data retrieved from database to pandas dataframe'''

for i in data:
    t = i["datetime"]
    if '.' in t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
    list_datetimes.append(t.astimezone(tz))

    list_temperatures.append(round(float(i["temperature"]), 1))


last_temp = list_temperatures[-1]
pre_last_temp = list_temperatures[-2]
delta_temps = round(last_temp - pre_last_temp, 1)

df = pd.DataFrame(data={
    'Ημερομηνία/ώρα': list_datetimes,
    'Θερμοκρασία': list_temperatures
})
df['Ημερομηνία'] = df['Ημερομηνία/ώρα'].dt.strftime('%d %b %y')
df['Ώρα'] = df['Ημερομηνία/ώρα'].dt.strftime('%H:%M')
df['Μήνας/Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%m/%y')
df['Ημέρα του μήνα'] = df['Ημερομηνία/ώρα'].dt.strftime('%d')

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
    f'μέγιστη: **{today_max["Θερμοκρασία"]} °C** :clock1: :red-background[{ttt}]'
    f'ελάχιστη: **{today_min["Θερμοκρασία"]} °C** :clock1: :blue-background[{ddd}]'
    '---'
    f'χθες ίδια ώρα: **{yesterday_same_time} °C**'

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
    st.dataframe(filtered_df
                 .style.highlight_max(axis=0, subset=['Θερμοκρασία'], props='background-color:red;')
                 .highlight_min(axis=0, subset=['Θερμοκρασία'], props='background-color:blue;'),
                 column_order=["Ώρα", "Θερμοκρασία"],
                 hide_index=True,
                 use_container_width=True)


def go_to_next_month():
    global selected_month
    selected_month = selected_month + timedelta(days=30)


with tab_month:
    '''Λίστα με όλες τις ημέρες του μήνα (μέγιστη, ελάχιστη, μέση)'''
    try:
        selected_month
    except:
        selected_month = datetime.now()
    st.write(selected_month)
    filtered_df_month = df.loc[(df["Μήνας/Έτος"] == selected_month.strftime('%m/%y'))]
    c_month_1, c_month_2, c_month_3 = st.columns(3)
    with c_month_2:
        st.subheader(f'{datetime.now().strftime("%B")} {datetime.now().year}')
        st.line_chart(filtered_df_month, x="Ημέρα του μήνα", y="Θερμοκρασία")
        st.write(filtered_df_month)
    with c_month_1:
        st.button("Προηγούμενος Μήνας")
    with c_month_3:
        st.button(label="Επόμενος Μήνας", on_click=go_to_next_month)


# st.write(data)

st.image('https://lh3.googleusercontent.com/a/ACg8ocKf_BEQXNtWgvgzj2Jump2CMCB5dCo95RWSdQdsh_67Ga3prkYU=s288-c-no',
         caption='Designed by Kleanthis Xenitidis', width=100)
st.link_button("xenitidis.eu", "https://www.xenitidis.eu")