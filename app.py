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

selected = option_menu(None, ["Prediction", "Result"], 
    icons=['cloud-upload', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal",
)

if selected == "Prediction":
    generate_predict = st.button("Generate Prediction")
    if generate_predict:
        with st.spinner("Please wait around 10-15 minutes due many data"):   
            st.session_state.result = fc.run_prediction()

if selected == "Result":
    prediction_result = st.button("Show Prediction Result")
    if prediction_result:
        st.write("5 Sample Data Bulan Desember 2016 untuk semua Produk")
        result = fc.get_predicted_data()
        st.table(result.head(5))
        st.download_button(
                    "Download Prediction Data",
                    result.to_csv(index=False).encode("utf-8"), 
                    file_name=f"prediction_result.csv",
                    mime='text/csv')