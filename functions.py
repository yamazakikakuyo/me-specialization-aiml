from google.cloud import bigquery
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import pandas as pd
import numpy as np
import json
from datetime import datetime

PROJECT_ID = "me-specialization-aiml"
LOCATION_ID = "us-central1"
LOCATION_ID_2 = "US"

client_bigquery = bigquery.Client(project=PROJECT_ID, location=LOCATION_ID)
aiplatform.init(project=PROJECT_ID, location=LOCATION_ID)
client_options = {"api_endpoint": f"{LOCATION_ID}-aiplatform.googleapis.com"}
client_jobservice = aiplatform.gapic.JobServiceClient(client_options=client_options)

def batch_prediction(
    project: str,
    location: str,
    model_resource_name: str,
    job_display_name: str,
    bigquery_source: str,
    bigquery_destination_prefix: str,
):
    my_model = aiplatform.Model(model_resource_name)

    batch_prediction_job = my_model.batch_predict(
        job_display_name=job_display_name,
        bigquery_source=bigquery_source,
        bigquery_destination_prefix=bigquery_destination_prefix,
        sync=False,
    )
    batch_prediction_job.wait_for_resource_creation()
    return batch_prediction_job

def get_predicted_data(result_option):
    table_name = ''
    # if result_option == "1 Month":
    if result_option == "With Feature Engineering":
        table_name = "predictions_2024_06_20T06_39_18_417Z_905"
    else:
        table_name = "predictions_2024_06_20T06_37_20_017Z_768"
    query = """
    SELECT Product_Code, Date, predicted_Order_Demand.value
    FROM `me-specialization-aiml.output_batch_predict.{}`
    """.format(table_name)

    # Menjalankan query dan mengambil hasil
    client_bigquery = bigquery.Client(project=PROJECT_ID, location=LOCATION_ID)
    query_job = client_bigquery.query(query)
    results = query_job.result().to_dataframe()

    # Mengonversi kolom Date menjadi datetime dan menghilangkan waktu
    results['Date'] = pd.to_datetime(results['Date']).dt.date

    # Replace negative values in the 'Predicted_Order_Demand' column with 0
    results['Predicted_Order_Demand'] = results['value'].apply(lambda x: max(x, 0) if np.issubdtype(type(x), np.number) else x)
    results = results.drop(columns=['value'])
    return results

def get_real_data(result_option):
    table_name = ''
    if result_option == "With Feature Engineering":
        table_name = "dataset_automl"
    else:
        table_name = "fe_dataset_automl"
    query = """
    SELECT Product_Code, Date, Order_Demand
    FROM `me-specialization-aiml.demand_dataset.{}`
    """.format(table_name)

    # Menjalankan query dan mengambil hasil
    client_bigquery = bigquery.Client(project=PROJECT_ID, location=LOCATION_ID_2)
    query_job = client_bigquery.query(query)
    results = query_job.result().to_dataframe()

    # Mengonversi kolom Date menjadi datetime dan menghilangkan waktu
    results['Date'] = pd.to_datetime(results['Date']).dt.date
    
    return results

def run_prediction(pred_option):
    if pred_option == "With Feature Engineering":
        obj_batch_pred = batch_prediction(
            project=PROJECT_ID,
            location=LOCATION_ID,
            model_resource_name="8557834350027079680",
            job_display_name="fe_demand_forecast_1_month",
            bigquery_source="bq://me-specialization-aiml.demand_dataset_2.dataset_testing",
            bigquery_destination_prefix="bq://me-specialization-aiml.output_batch_predict",
        )
    else:
        obj_batch_pred = batch_prediction(
            project=PROJECT_ID,
            location=LOCATION_ID,
            model_resource_name="5911969568946913280",
            job_display_name="demand_forecast_1_months",
            bigquery_source="bq://me-specialization-aiml.demand_dataset_2.fe_dataset_testing",
            bigquery_destination_prefix="bq://me-specialization-aiml.output_batch_predict",
        )

def get_list_batch_prediction_job():
    request = aiplatform.gapic.ListBatchPredictionJobsRequest(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION_ID}",
    )
    page_result = client_jobservice.list_batch_prediction_jobs(request=request)

    state_name = {
        "JOB_STATE_UNSPECIFIED": "Unspecified",
        "JOB_STATE_QUEUED": "Just created or resumed and processing has not yet begun.",
        "JOB_STATE_PENDING": "Preparing to run prediction.",
        "JOB_STATE_RUNNING": "Prediction is on progress.",
        "JOB_STATE_SUCCEEDED": "Prediction completed successfully.",
        "JOB_STATE_FAILED": "Predicition job failed.",
        "JOB_STATE_CANCELLING": "Prediction is on progress.",
        "JOB_STATE_CANCELLED": "Prediction has been cancelled.",
        "JOB_STATE_PAUSED": "Prediction has been stopped, and can be resumed.",
        "JOB_STATE_EXPIRED": "Prediction has expired.",
        "JOB_STATE_UPDATING": "Prediction is being updated",
        "JOB_STATE_PARTIALLY_SUCCEEDED": "Prediction is partially succeeded, some results may be missing due to errors."}

    result = []
    for x in page_result:
        result.append({
            "Creation Time": datetime.fromtimestamp(int(x.create_time.timestamp())).strftime("%A, %d %B %Y, %I:%M:%S"),
            "Name": x.display_name, 
            "Input": x.input_config.bigquery_source.input_uri, 
            "Output": x.output_info.bigquery_output_dataset + '.' + x.output_info.bigquery_output_table,
            "State": state_name[x.state.name]
        })

    return pd.DataFrame(result, columns=["Creation Time", "Name", "Input", "Output", "State"])

def get_evaluation_detail(result_type):
    if result_type == "With Feature Engineering":
        my_model = aiplatform.Model("8557834350027079680")
    else:
        my_model = aiplatform.Model("5911969568946913280")
    return my_model.get_model_evaluation().to_dict()['metrics']