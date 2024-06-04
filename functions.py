from google.cloud import bigquery
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import json

PROJECT_ID = "me-specialization-aiml"

client_bigquery = bigquery.Client(project=PROJECT_ID, location='asia-southeast2')
aiplatform.init(project=PROJECT_ID, location='asia-southeast2')

def batch_prediction(
    project: str,
    location: str,
    model_resource_name: str,
    job_display_name: str,
    bigquery_source: str,
    bigquery_destination_prefix: str, #dia otomatis ngebuat tabel baru, cukup masukan project dan dataset. contoh : "me-specialization-aiml.demand_batch_forecast"
    sync: bool = True,
):
    my_model = aiplatform.Model(model_resource_name)

    batch_prediction_job = my_model.batch_predict(
        job_display_name=job_display_name,
        bigquery_source=bigquery_source,
        bigquery_destination_prefix=bigquery_destination_prefix,
        sync=sync,
    )

    batch_prediction_job.wait()

    print(batch_prediction_job.display_name)
    print(batch_prediction_job.resource_name)
    print(batch_prediction_job.state)
    print(batch_prediction_job.output_info)
    return batch_prediction_job

def get_predicted_data(obj_batch_pred):
    query = """
    SELECT Product_Code, Month, Date, Predicted_Order_Demand
    FROM `{}.{}`
    """.format(
        obj_batch_pred.output_info.bigquery_output_dataset, 
        obj_batch_pred.output_info.bigquery_output_table
    )

    # Menjalankan query dan mengambil hasil
    query_job = bigquery_client.query(query)
    results = query_job.result().to_dataframe()

    # Mengonversi kolom Date menjadi datetime dan menghilangkan waktu
    results['Date'] = pd.to_datetime(results['Date']).dt.date

    # Replace negative values in the 'Predicted_Order_Demand' column with 0
    results['Predicted_Order_Demand'] = results['Predicted_Order_Demand'].apply(lambda x: max(x, 0) if np.issubdtype(type(x), np.number) else x)

    return results

def run_prediction():
    obj_batch_pred = batch_prediction(
        project=PROJECT_ID,
        location="asia-southeast2",
        model_resource_name="577146847559155712",
        job_display_name="monthly_demand_forecast",
        bigquery_source="bq://me-specialization-aiml.demand_dataset.dataset_testing",
        bigquery_destination_prefix="bq://me-specialization-aiml.demand_batch_forecast",
    )

    result = get_predicted_data(obj_batch_pred)

    return result
