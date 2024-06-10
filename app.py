import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import functions as fc
import time
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Stock Prediction AutoML",
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

if "result" not in st.session_state:
    st.session_state.result = None

if "result_type" not in st.session_state:
    st.session_state.result_type = None

if "list_items" not in st.session_state:
    st.session_state.list_items = None

if "real_value" not in st.session_state:
    st.session_state.real_value = None

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
    pred_option = st.selectbox(
        "How long you want to predict?",
        ("1 Month", "3 Months")
    )
    generate_predict = st.button("Generate Prediction")
    if generate_predict: 
        st.session_state.result = fc.run_prediction(pred_option)
    st.table(fc.get_list_batch_prediction_job())

if selected == "Result":
    result_option = st.selectbox(
        "How long you want to predict?",
        ("1 Month", "3 Months")
    )
    prediction_result = st.button("Show Prediction Result")
    if prediction_result:
        st.session_state.result = fc.get_predicted_data(result_option)
        st.session_state.result_type = result_option
        st.session_state.list_items = list(set(st.session_state.result['Product_Code'].values))
        st.session_state.real_value = fc.get_real_data(result_option)
    
    if type(st.session_state.result) != type(None):
        st.write(f"5 Sample Prediction for {st.session_state.result_type}")
        st.table(st.session_state.result.head(5))
        pred_option = st.selectbox(
            "How long you want to predict?",
            st.session_state.list_items
        )
        generate_graph = st.button("Generate Graph")
        st.download_button(
                    "Download Prediction Data",
                    st.session_state.result.to_csv(index=False).encode("utf-8"), 
                    file_name=f"prediction_result.csv",
                    mime='text/csv')
        if generate_graph:
            real_data = st.session_state.real_value[st.session_state.real_value['Product_Code'] == pred_option]
            pred_data = st.session_state.result[st.session_state.result['Product_Code'] == pred_option].sort_values(by=["Date"])
            real_data = real_data[~(real_data['Date'].isin(pred_data['Date']))].sort_values(by=["Date"])
            plt.figure(figsize=(20, 5))
            plt.plot(pd.concat([real_data['Date'], pred_data['Date']]), pd.concat([real_data['Order_Demand'], pred_data['Predicted_Order_Demand']]), label='Predicted Data', color='orange')
            plt.plot(real_data['Date'], real_data['Order_Demand'], label='Real Data', color='blue')
            plt.xlabel('Month')
            plt.ylabel('Sales')
            plt.title(f'Prediction of {pred_option} for {st.session_state.result_type}')
            plt.legend()
            st.pyplot(plt)
