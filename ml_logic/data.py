import pandas as pd

from google.cloud import bigquery
from google.oauth2 import service_account

from ml_logic.params import GCP_PROJECT, CREDENTIAL_PATH, REVIEW_TABLE_ID

def get_random_news(user_id:int, categories:list, nb_news:int=20):
    """
    Retrieve <nb_news> random news not viewed by <user_id> and
    in the <categories> list and return a DataFrame
    """
    # Create credentials and client using the key file
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT)

    params = [
    bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
    bigquery.ScalarQueryParameter("nb_news", "INT64", nb_news),
    bigquery.ArrayQueryParameter("category_ids", "INT64", categories),
    ]

    query = """
    WITH CombinedNews AS (
        SELECT *,
               ROW_NUMBER() OVER(ORDER BY RAND()) AS rand_num
        FROM `the-mdr-project.live_mdr.news_dataset`
        WHERE category_id IN UNNEST(@category_ids)
            AND news_id NOT IN (
                SELECT news_id
                FROM `the-mdr-project.live_mdr.review_dataset`
                WHERE user_id = @user_id
            )
    )
    SELECT *
    FROM CombinedNews
    WHERE rand_num <= @nb_news;
    """

    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = params

    query_job = client.query(query, job_config=job_config)

    result = query_job.result().to_dataframe()

    return result

def save_feedback(feedback:dict):
    """
    Retrieve feedback from front and save information in review table
    """
    # Create credentials and client using the key file
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT)

    # Create DataFrame
    feedback_df = pd.DataFrame.from_dict(feedback)

    # Save in BQ
    write_mode = 'WRITE_APPEND'
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
    job = client.load_table_from_dataframe(feedback_df, REVIEW_TABLE_ID, job_config=job_config)
    result = job.result()
    return result


def get_recommended_news(user_id:int):
    pass
