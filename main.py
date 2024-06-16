import os
import streamlit as st
from supabase import create_client, Client


url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

supabase = create_client(url, key)

response = supabase.table('roof_temperature').select("*").execute()

st.header("Weather Station")


st.write(response)

