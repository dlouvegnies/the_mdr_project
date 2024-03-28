from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import pymysql
from ml_logic.params import DB_SERVER, USER_DB, PASSWORD_DB, DB_NAME, CACHE_VALIDATION_DURATION
import pandas as pd
from ml_logic.model import Model
import os
import numpy as np
from datetime import datetime,timedelta
from ml_logic.category import Category

from ml_logic.recommendation import get_top_similar_news
from ml_logic.data_mysql import db_to_dataframe
from ml_logic.category import Category

class Cache_Bert:

    def __init__(self,user_id):
        self.user_id = user_id
        self.connector = Connector()

    """
    Return a news from the cache for evaluation
    """
    def get_one_news_for_evaluation(self, news_df, method, caterory_id=0):

        cat_obj = Category(self.user_id)
        CAT_ID=cat_obj.get_user_categories_ids()

        #Regarde si le cache existe pour le user
        self.check_valid_cache(news_df, CACHE_VALIDATION_DURATION,CAT_ID, method)

        sql_query = f"SELECT * FROM cached_news_dataset WHERE user_id ={self.user_id}"
        df=self.execute_query_with_df_as_result_no_params(sql_query)
        print(df)

        #Check if we have a news for that category_id
        df_cat = df.loc[df["category_id"]==caterory_id]
        if len(df_cat)>0:
            the_news = df_cat.iloc[0].to_frame().to_dict()
        else :
            the_news = df.iloc[0].to_frame().to_dict()

        news_id = df.iloc[0]["news_id"]
        self.remove_one_news_from_cache(news_id)
        print(news_id)
        return the_news



    """
    Clear the cache for the user
    """
    def clear_user_cache(self):
        sql_query = f"DELETE FROM cached_news_dataset WHERE user_id ={self.user_id}"
        self.execute_query(text(sql_query))
        print("Clear one cache done")


    """
    Clear all caches of evry uses
    """
    def clear_all_caches(self):
        sql_query = f"DELETE FROM cached_news_dataset "
        self.execute_query(text(sql_query))
        print("Clear all caches done")


    """
    Remove the news_id from the user's cache
    """
    def remove_one_news_from_cache(self,news_id):
        sql_query = f"DELETE FROM cached_news_dataset  WHERE user_id ={self.user_id} AND news_id={news_id}"
        self.execute_query(text(sql_query))
        print("Clear one news done")




    def check_valid_cache(self, news_df, cache_minutes:int,categories:list, method):

        maintenant = datetime.now()
        moment_dans_le_passe = maintenant - timedelta(minutes=cache_minutes)
        # Formater l'instant dans le passé dans le format requis
        moment_dans_le_passe_formatte = moment_dans_le_passe.strftime('%Y-%m-%d %H:%M:%S')

        sql_query = f"SELECT count(*) FROM cached_news_dataset  WHERE user_id ={self.user_id} AND cached_date > '{moment_dans_le_passe_formatte}'  "

        nb_valid_news_in_cache = self.execute_query(text(sql_query)).fetchone()[0]
        print(nb_valid_news_in_cache)
        if nb_valid_news_in_cache<1 :
            self.clear_user_cache()
            self.create_bert_cache(news_df, categories, method)
            print("Cache checked")

    """
    Create the user's cache
    """
    def create_bert_cache(self, news_df, categories:list, method):
        #STEP 1 : get All the news and recommendation his liked
        sql_query = """
            SELECT n.*
            FROM review_dataset r
            JOIN news_dataset n
            ON r.news_id = n.news_id
            WHERE r.user_id = %(user_id)s
            AND n.category_id IN %(category_ids)s
            AND (r.like_the_news = TRUE OR r.good_recommendation = TRUE)
            ORDER BY r.updated_date DESC, n.added_date DESC
            """
        params={'category_ids': categories, 'user_id': self.user_id}
        liked_news_df = self.execute_query_with_df_as_result(sql_query,params)

        #STEP 2 : For each news, get recommendation

        # Obtenir l'instant présent
        maintenant = datetime.now()
        # Formater l'instant présent dans le format requis
        cached_date = maintenant.strftime('%Y-%m-%d %H:%M:%S')

        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)

        df_existing_review=self.get_reviewed_news()
        list_reco=[]
        with pool.connect() as db_conn :
            for index, row in liked_news_df.head(15).iterrows():
                embedding_array = np.frombuffer(row['embedding'], dtype=np.float64)
                recommendation_df = get_top_similar_news(embedding_array, news_df, num_recommendations=3, method=method)
                print('liked', row['title'], row['news_id'])
                print('reco', recommendation_df['title'])
                list_reco.append(recommendation_df)
            merged_recommendations = pd.concat(list_reco, ignore_index=True)
            merged_recommendations.drop_duplicates(subset=['news_id'], inplace=True)
            mask = merged_recommendations['news_id'].isin(df_existing_review['news_id'])
            filtered_merged_recommendations = merged_recommendations[~mask]
            filtered_merged_recommendations.insert(0, 'cached_date', cached_date)
            filtered_merged_recommendations.insert(1, 'user_id', self.user_id)
            filtered_merged_recommendations.drop(columns=['embedding'], inplace=True)
            filtered_merged_recommendations.to_sql(name='cached_news_dataset', con=db_conn, if_exists='append', index=False)


    #NOT USEFUL
    def news_not_evaluated(self,news_id):
        sql_query = f"SELECT count(*) FROM review_dataset  WHERE user_id ={self.user_id} AND news_id={news_id} "
        present = self.execute_query(text(sql_query)).fetchone()[0]
        print(f"news_not_evaluated --{news_id}")
        return present>0


    def get_reviewed_news(self):
        sql_query = f"SELECT * FROM review_dataset  WHERE user_id ={self.user_id}"
        df_existing_review=self.execute_query_with_df_as_result_no_params(sql_query)
        return df_existing_review


    def execute_query(self,sql_query):
        # create connection pool
        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)
        db_conn = pool.connect()
        with pool.connect() as db_conn :
            rep=db_conn.execute(sql_query)
            db_conn.commit()
        return rep

    def execute_query_with_df_as_result(self,sql_query,params={}):
        # create connection pool
        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)
        db_conn = pool.connect()
        with pool.connect() as db_conn :
            result = pd.read_sql_query(sql_query, db_conn, params=params)
        return result

    def execute_query_with_df_as_result_no_params(self,sql_query):
        # create connection pool
        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)
        db_conn = pool.connect()
        with pool.connect() as db_conn :
            result = pd.read_sql_query(sql_query, db_conn)
        return result

        # function to return the database connection
    def getconn(self) -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = self.connector.connect(DB_SERVER,"pymysql",user=USER_DB,password=PASSWORD_DB,db=DB_NAME,charset='utf8mb4',collation='utf8mb4_unicode_ci')
        return conn


# Code de test de la méthode GO
if __name__ == "__main__":
    # Création d'une instance de la classe TOTO
    cache_test = Cache_Bert(3)
    cache_test.clear_all_caches()
    news_df = db_to_dataframe(nb_rows=1000) #db_to_dataframe(date=datetime(2024, 3, 26))
