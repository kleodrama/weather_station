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

list_datetimes = list()
list_temperatures = list()


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
df['Μήνας/Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%m/%Y')
df['Μήν/Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%-m/%Y')
df['Έτος'] = df['Ημερομηνία/ώρα'].dt.strftime('%Y')
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
    f'μέγιστη: :thermometer: **{today_max["Θερμοκρασία"]} °C** :clock1: :red-background[{ttt}]'
    f'ελάχιστη: :thermometer: **{today_min["Θερμοκρασία"]} °C** :clock1: :blue-background[{ddd}]'
    # st.markdown("***")
    f'χθες ίδια ώρα: :thermometer: **{yesterday_same_time} °C**'

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
        st.dataframe(filtered_df
                    .style.highlight_max(axis=0, subset=['Θερμοκρασία'], props='background-color:red;')
                    .highlight_min(axis=0, subset=['Θερμοκρασία'], props='background-color:blue;'),
                    column_order=["Ώρα", "Θερμοκρασία"],
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
        current_values = df.loc[filtered_df_month["Ημέρα του μήνα"] == f'{i}']
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
    chart_data = pd.DataFrame(min_max_mean, columns=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"])
    st.line_chart(chart_data, x="Ημέρα", y=["Ελάχιστη", "Μέση", "Μέγιστη"])
    st.subheader(f'{month}/{year}', divider='rainbow')
    st.dataframe(min_max_mean, column_order=["Ημέρα", "Ελάχιστη", "Μέση", "Μέγιστη"], hide_index=True, use_container_width=True)

with tab_year:
    # if 'yyear' in st.session_state:
    #     yyear = st.session_state['yyear']
    #     selected_year = datetime.now().replace(year=yyear)
    # else:
    #     selected_year = datetime.now()
    #     st.session_state['yyear'] = datetime.now().year
    option = st.selectbox("Επιλογή έτους", pd.unique(df["Έτος"]))
    st.write("Επιλεγμένο έτος: ", option)
    filtered_df_year = df.loc[df["Έτος"] == f'{option}']
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
    st.subheader(f'{option}', divider='rainbow')
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
# st.write(data)

'---'

st.image('https://lh3.googleusercontent.com/a/ACg8ocKf_BEQXNtWgvgzj2Jump2CMCB5dCo95RWSdQdsh_67Ga3prkYU=s288-c-no',
         caption='Designed by Kleanthis Xenitidis', width=100)
st.link_button("xenitidis.eu", "https://www.xenitidis.eu")