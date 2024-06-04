import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import functions as fc
import time

st.set_page_config(
    page_title="SQL Talk with BigQuery",
    page_icon="metrodata-icon.png",
    layout="wide",
)

st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                width: 42% !important; # Set the width to your desired value
            }
            button[title="View fullscreen"]{
                visibility: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

if "result" not in st.session_state:
    st.session_state.result = None

# Initialize session state keys if they don't exist

# Function to reset the success message and related state variables
def reset_state():
    st.rerun()

col1, col2 = st.columns([8, 1])
with col1:
    st.title("Stock Prediction AutoML - ME Specialization AI/ML")
with col2:
    subcol1, subcol2, subcol3 = st.columns([1, 1, 1])
    with subcol1:
        st.image("google-icon.png")
    with subcol2:
        st.image("vertex-ai.png")
    with subcol3:
        st.image("metrodata-icon.png")

st.success(
    "Forecast based on data you upload with ease!",
    icon="📈",
)
col3, col4 = st.columns([1, 1])
with st.spinner("Please wait around 10-15 minutes due many data"):
    with col3:
        generate_predict = st.button("Generate Prediction")
        if st.session_state.result:
            download_button = st.button("Download Data")

    if generate_predict:    
            st.session_state.result = fc.run_prediction()

if st.session_state.result != None:
    st.write("Data Bulan Desember 2016 untuk semua Produk")
    st.table(st.session_state.result.head(5))
    st.download_button(
                "Download Prediction Data",
                st.session_state.result.to_csv(index=False).encode("utf-8"), 
                file_name=f"prediction_result.csv",
                mime='text/csv')