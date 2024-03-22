import numpy as np
import pandas as pd
from ml_logic.data_mysql import getconn
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

def create_user(user:dict):
    # Create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )

    conn = pool.connect()

    params={'username': user["username"], 'password': user["password"]}

    query = """
        SELECT * FROM the-mdr-project.live_mdr.user_dataset
        WHERE (username = %(username)s AND password = %(password)s);
        """

    result = pd.read_sql_query(query, conn, params=params)

    if not result.empty:
        return -1 # Already exist
    else:
        # Create DataFrame
        user_df = pd.DataFrame.from_dict(params)

        with pool.connect() as conn:
            try:
                user_df.to_sql(name='user_dataset', con=conn, if_exists='append', index=False)
                return True
            except SQLAlchemyError:
                return False
