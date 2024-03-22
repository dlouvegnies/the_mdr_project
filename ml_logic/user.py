import numpy as np

from google.cloud import bigquery
from google.oauth2 import service_account

from ml_logic.params import GCP_PROJECT, CREDENTIAL_PATH

def create_user(user:dict):
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT)

    user_id = np.random.randint(100, 200)

    params = [
    bigquery.ScalarQueryParameter("username", "STRING", user["username"]),
    bigquery.ScalarQueryParameter("password", "STRING", user["password"]),
    bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
    ]

    query = """
        SELECT * FROM the-mdr-project.live_mdr.user_dataset
        WHERE (username = @username AND password = @password);
        """

    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = params

    query_job = client.query(query, job_config=job_config)

    result = query_job.result().to_dataframe()
    if not result.empty:
        return -1 # Already exist
    else:
        insert_query = """INSERT INTO the-mdr-project.live_mdr.user_dataset (user_id, username, password)
            VALUES (@user_id, @username, @password);"""
        insert_job_config = bigquery.QueryJobConfig(query_parameters=params)
        insert_query_job = client.query(insert_query, job_config=insert_job_config)
        insert_result = insert_query_job.result()
        if insert_result:
            return 1 # Success
        else:
            return 0 # Failed



def connect_user(user:dict):
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT)

    params = [
    bigquery.ScalarQueryParameter("username", "STRING", user["username"]),
    bigquery.ScalarQueryParameter("password", "STRING", user["password"]),
    ]

    query = """
        SELECT * FROM the-mdr-project.live_mdr.user_dataset
        WHERE (username = @username AND password = @password);
        """

    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = params

    query_job = client.query(query, job_config=job_config)

    result = query_job.result().to_dataframe()
    if result.empty:
        return 0 #Doesn't exist
    else:
        return 1
