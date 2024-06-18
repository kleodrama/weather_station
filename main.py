import os
import streamlit as st
from supabase import create_client, Client
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
import pytz
tz = pytz.timezone('Europe/Athens')


url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

supabase = create_client(url, key)

response = supabase.table('roof_temperature').select("*").execute()
data = response.data

list_datetimes = list()
list_temperatures = list()

'''TODO: function that converts data retrieved from database to pandas dataframe'''
for i in data:
    t = i["datetime"]
    if '.' in t:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S%z")
    list_datetimes.append(t.astimezone(tz))

    list_temperatures.append(round(float(i["temperature"]), 1))

df = pd.DataFrame(data={
    'Ημερομηνία/ώρα': list_datetimes,
    'Θερμοκρασία': list_temperatures
})
df['Ημερομηνία'] = df['Ημερομηνία/ώρα'].dt.strftime('%d %b %y')

st.write(df)

st.line_chart(df, y="Θερμοκρασία", x='Ημερομηνία/ώρα')

# st.header("Weather Station")

tab_day, tab_month, tab_year = st.tabs(["Σήμερα", "Μηνιαία", "Ετήσια"])

with tab_day:
    df['Ώρα'] = df['Ημερομηνία/ώρα'].dt.strftime('%H:%M')
    td = datetime.today()
    st.write("Σήμερα ", td.weekday(), td.day, td.month, td.year)
    day = st.date_input("Επιλογή ημέρας"
                        , value="default_value_today"
                        , format="DD/MM/YYYY"
                        )
    next_day = day + timedelta(days=1)
    st.write("Επιλεγμένη ημερομηνία: ", day)
    filtered_df = df.loc[(df["Ημερομηνία/ώρα"] >= day.strftime('%Y-%m/%d')) & (df["Ημερομηνία/ώρα"] <=
                                                                               next_day.strftime('%Y-%m/%d'))]
    st.line_chart(filtered_df, y="Θερμοκρασία", x='Ώρα')
    st.dataframe(filtered_df
                 .style.highlight_max(axis=0, subset=['Θερμοκρασία'], props='background-color:red;')
                 .highlight_min(axis=0, subset=['Θερμοκρασία'], props='background-color:blue;'),
                 column_order=["Ώρα", "Θερμοκρασία"],
                 hide_index=True,
                 use_container_width=True)


st.write(data)

