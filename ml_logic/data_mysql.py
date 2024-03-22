from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pymysql
import pandas as pd

from ml_logic.params import DB_SERVER, USER_DB, PASSWORD_DB, DB_NAME, CATEGORIES_ID

def getconn() -> pymysql.connections.Connection:
    """
    Return the database connection
    """
    connector = Connector()
    conn: pymysql.connections.Connection = connector.connect(
        DB_SERVER,
        "pymysql",
        user=USER_DB,
        password=PASSWORD_DB,
        db=DB_NAME
    )
    return conn


def get_random_news(user_id:int, categories:list=CATEGORIES_ID, nb_news:int=20):
    """
    Retrieve <nb_news> random news not viewed by <user_id> and
    in the <categories> list and return a DataFrame
    """
    # Create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    conn = pool.connect()

    params={'category_ids': categories, 'user_id': user_id, 'nb_news': nb_news}

    query = """
    WITH CombinedNews AS (
        SELECT *,
               ROW_NUMBER() OVER(ORDER BY RAND()) AS rand_num
        FROM news_dataset
        WHERE category_id IN %(category_ids)s
            AND news_id NOT IN (
                SELECT news_id
                FROM review_dataset
                WHERE user_id = %(user_id)s
            )
    )
    SELECT *
    FROM CombinedNews
    WHERE rand_num <= %(nb_news)s;
    """

    result = pd.read_sql_query(query, conn, params=params)

    return result


def save_feedback(feedback:dict):
    """
    Retrieve feedback from front and save information in review table
    """
    # Create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )

    # Create DataFrame
    feedback_df = pd.DataFrame.from_dict(feedback)
    feedback_df['updated_date'] = pd.to_datetime(feedback_df["updated_date"])

    with pool.connect() as conn:
        try:
            feedback_df.to_sql(name='review_dataset', con=conn, if_exists='append', index=False)
            return True
        except SQLAlchemyError:
            return False


def get_last_news_liked(user_id:int, categories:list):
    """
    Return the last news like by an user for given categories
    """
    # Create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    conn = pool.connect()

    params={'category_ids': categories, 'user_id': user_id}

    query = """
    SELECT n.*
    FROM review_dataset r
    JOIN news_dataset n
    ON r.news_id = n.news_id
    WHERE r.user_id = %(user_id)s
    AND category_id IN %(category_ids)s
    AND (r.like_the_news = TRUE OR r.good_recommendation = TRUE)
    ORDER BY r.updated_date DESC
    LIMIT 1
    """

    result = pd.read_sql_query(query, conn, params=params)

    print('------------LAST NEWS LIKED BY {user_id} retrieve -------------')
    print(result)
    print('-------------------------')
    return result


def db_to_dataframe(nb_rows=20000):
    """
    Retrieve data from big query with <nb_rows> and return it in DataFrame
    """
    # Create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    conn = pool.connect()

    if nb_rows is not None:
        params={'nb_rows': nb_rows}
        limit_clause = "LIMIT %(nb_rows)s"
    else:
        limit_clause = ""


    query = f"""SELECT *
                FROM news_dataset order by added_date DESC
                {limit_clause}
            """
    if nb_rows is not None:
        result = pd.read_sql_query(query, conn, params=params)
    else:
        result = pd.read_sql_query(query, conn)
    print("DataFrame retrieve from MySQL")
    return result
