from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pymysql
import pandas as pd
import numpy as np
from datetime import datetime

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


def db_to_dataframe(date=None, nb_rows=None):
    """
    Retrieve data from big query with <nb_rows> and return it in DataFrame
    """
    # Create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    conn = pool.connect()

    params = {}
    if date is not None:
        params['date']= date.strftime("%Y-%m-%d")
        where_clause = "WHERE added_date <= %(date)s" # Remettre le >
    else:
        where_clause = ""

    if nb_rows is not None:
        params['nb_rows'] = nb_rows
        limit_clause = "LIMIT %(nb_rows)s"
    else:
        limit_clause = ""


    query = f"""SELECT *
                FROM news_dataset
                {where_clause}
                ORDER BY added_date DESC
                {limit_clause}
            """
    if nb_rows is not None or date is not None:
        result = pd.read_sql_query(query, conn, params=params)
    else:
        result = pd.read_sql_query(query, conn)
    print("DataFrame retrieve from MySQL")
    print(result)
    result['embedding'] = result['embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32).tolist())
    print("Embedding decoded")
    return result
