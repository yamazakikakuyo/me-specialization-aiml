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
        evaluation = fc.get_evaluation_detail(st.session_state.result_type)
        with st.container(border=True):
            st.write("**Evaluation Result**")
            eval_col1, eval_col2, eval_col3, eval_col4 = st.columns([1,1,1,1])
            with eval_col1:
                st.write(f"RMSLE : {evaluation['rootMeanSquaredLogError']}")
                st.write(f"RMSPE : {evaluation['rootMeanSquaredPercentageError']}")
            with eval_col2:
                st.write(f"MAPE : {evaluation['meanAbsolutePercentageError']}")
                st.write(f"WAPE : {evaluation['weightedAbsolutePercentageError']}")
            with eval_col3:
                st.write(f"RMSE : {evaluation['rootMeanSquaredError']}")
                st.write(f"R^2 : {evaluation['rSquared']}")
            with eval_col4:
                st.write(f"MAE : {evaluation['meanAbsoluteError']}")
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
            # plt.figure(figsize=(20, 5))
            # plt.plot(pd.concat([real_data['Date'], pred_data['Date']]), pd.concat([real_data['Order_Demand'], pred_data['Predicted_Order_Demand']]), marker='o', label='Predicted Data', color='orange')
            # plt.plot(real_data['Date'], real_data['Order_Demand'], marker='o', label='Real Data', color='blue')
            # plt.xlabel('Month')
            # plt.ylabel('Sales')
            # plt.title(f'Prediction of {pred_option} for {st.session_state.result_type}')
            # plt.grid()
            # plt.legend()
            # st.pyplot(plt)

            fig = plt.figure(figsize=(15, 5))
            plt.plot(pd.concat([real_data['Date'], pred_data['Date']]), pd.concat([real_data['Order_Demand'], pred_data['Predicted_Order_Demand']]), marker='o', label='Predicted Data', color='orange')
            plt.plot(real_data['Date'], real_data['Order_Demand'], marker='o', label='Real Data', color='blue')
            plt.xlabel('Date')
            plt.ylabel('Order Demand')
            plt.title(f'Prediction of {pred_option} for {st.session_state.result_type}')
            plt.grid()
            plt.legend()
            css = """
            table
            {
            border-collapse: collapse;
            }
            th
            {
            color: #ffffff;
            background-color: #000000;
            }
            td
            {
            background-color: #cccccc;
            }
            table, th, td
            {
            font-family:Arial, Helvetica, sans-serif;
            border: 1px solid black;
            text-align: right;
            }
            """
            print(fig.axes[0].get_lines())
            for axes in fig.axes:
                for line in axes.get_lines():
                    # get the x and y coords
                    # print(line.get_xdata())
                    xy_data = line.get_data()
                    labels = []
                    for x, y in list(zip(xy_data[0], xy_data[1])):
                        # Create a label for each point with the x and y coords
                        html_label = f'<table border="1" class="dataframe"> <thead> <tr style="text-align: right;"> </thead> <tbody> <tr> <th>Date</th> <td>{x.strftime("%d-%m-%Y")}</td> </tr> <tr> <th>Order Demand</th> <td>{y}</td> </tr> </tbody> </table>'
                        labels.append(html_label)
                    # Create the tooltip with the labels (x and y coords) and attach it to each line with the css specified
                    tooltip = mpld3.plugins.PointHTMLTooltip(line, labels, css=css)
                    # Since this is a separate plugin, you have to connect it
                    mpld3.plugins.connect(fig, tooltip)
            
            fig_html = mpld3.fig_to_html(fig)
            st.components.v1.html(fig_html, height=600)
