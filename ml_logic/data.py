import pandas as pd

from google.cloud import bigquery
from google.oauth2 import service_account

from ml_logic.params import GCP_PROJECT, CREDENTIAL_PATH, REVIEW_TABLE_ID,\
NEWS_TABLE_ID, LOCAL_URL, SERVICE_URL, CATEGORIES_ID

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
    feedback_df['updated_date'] = pd.to_datetime(feedback_df["updated_date"])

    # Save in BQ
    write_mode = 'WRITE_APPEND'
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
    job = client.load_table_from_dataframe(feedback_df, REVIEW_TABLE_ID, job_config=job_config)
    result = job.result()
    return result


def get_last_news_liked(user_id:int, categories:list=CATEGORIES_ID):
    """
    Return the last news like by an user
    """
    # Create credentials and client using the key file
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT)

    params = [
    bigquery.ScalarQueryParameter("user_id", "INT64", user_id),
    ]

    query = f"""
    SELECT n.*
    FROM {REVIEW_TABLE_ID} r
    JOIN {NEWS_TABLE_ID} n
    ON r.news_id = n.news_id
    WHERE r.user_id = @user_id
    AND (r.like_the_news = TRUE OR r.good_recommendation = TRUE)
    ORDER BY r.updated_date DESC
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = params

    query_job = client.query(query, job_config=job_config)

    result = query_job.result().to_dataframe()
    print('------------LAST NEWS LIKED BY {user_id} retrieve -------------')
    print(result.empty)
    print('-------------------------')
    return result


def db_to_dataframe(nb_rows=None):
    """
    Retrieve data from big query with <nb_rows> and return it in DataFrame
    """
    # Create credentials and client using the key file
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    client = bigquery.Client(credentials=credentials, project=GCP_PROJECT)

    if nb_rows is not None:
        params = [bigquery.ScalarQueryParameter("nb_rows", "INT64", nb_rows)]
        limit_clause = "LIMIT @nb_rows"
    else:
        limit_clause = ""

    query = f"""SELECT *
                FROM the-mdr-project.live_mdr.news_dataset
                {limit_clause}
            """

    job_config = bigquery.QueryJobConfig()
    if nb_rows is not None:
        job_config.query_parameters = params

    query_job = client.query(query, job_config=job_config)

    result = query_job.result().to_dataframe()
    print("DataFrame retrieve from BQ")
    return result
