from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import pymysql
from ml_logic.params import DB_SERVER,USER_DB,PASSWORD_DB,DB_NAME,CATEGORIES_ID,CACHE_VALIDATION_DURATION
import pandas as pd
from model import Model
import os
import numpy as np
from datetime import datetime,timedelta

class Cache:

    def __init__(self,user_id):
        self.user_id = user_id
        self.connector = Connector()

    """
    Return a news from the cache for evaluation
    """
    def get_one_news_for_evaluation(self,caterory_id=0):

        #Regarde si le cache existe pour le user
        self.check_valid_cache(CACHE_VALIDATION_DURATION,CATEGORIES_ID)

        sql_query = f"SELECT * FROM cached_news_dataset WHERE user_id ={self.user_id}"
        df=self.execute_query_with_df_as_result_no_params(sql_query)

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




    def check_valid_cache(self,cache_minutes:int,categories:list):

        maintenant = datetime.now()
        moment_dans_le_passe = maintenant - timedelta(minutes=cache_minutes)
        # Formater l'instant dans le passé dans le format requis
        moment_dans_le_passe_formatte = moment_dans_le_passe.strftime('%Y-%m-%d %H:%M:%S')

        sql_query = f"SELECT count(*) FROM cached_news_dataset  WHERE user_id ={self.user_id} AND cached_date > '{moment_dans_le_passe_formatte}'  "

        nb_valid_news_in_cache = self.execute_query(text(sql_query)).fetchone()[0]
        print(nb_valid_news_in_cache)
        if nb_valid_news_in_cache<1 :
            self.clear_user_cache()
            self.create_one_user_cache(categories)
            print("Cache checked")

    """
    Create the user's cache
    """
    def create_one_user_cache(self, categories:list):
        #STEP 1 : get All the news and recommendation his liked
        sql_query = """
            SELECT n.*
            FROM review_dataset r
            JOIN news_dataset n
            ON r.news_id = n.news_id
            WHERE r.user_id = %(user_id)s
            AND category_id IN %(category_ids)s
            AND (r.like_the_news = TRUE OR r.good_recommendation = TRUE)
            ORDER BY r.updated_date DESC, n.added_date DESC
            """
        params={'category_ids': categories, 'user_id': self.user_id}
        liked_news_df = self.execute_query_with_df_as_result(sql_query,params)

        #STEP 2 : For each news, get recommendation
        # Retrieve BQ data in Dataframe and cleaning it
        data_filename = os.path.join("raw_data", "data_for_model.csv")

        if os.path.exists(data_filename):
            news_df = pd.read_csv(data_filename)
            news_df.replace(np.nan, None, inplace=True)
        else:
            news_df = self.db_to_dataframe_cache()
            news_df = news_df.drop_duplicates()
            news_df.replace(np.nan, None, inplace=True)
            news_df.to_csv(data_filename, index=False)

        model = Model(news_df)
        # Obtenir l'instant présent
        maintenant = datetime.now()
        # Formater l'instant présent dans le format requis
        cached_date = maintenant.strftime('%Y-%m-%d %H:%M:%S')

        connector = Connector()
        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)

        list_reco=[]
        with pool.connect() as db_conn :
            for index, row in liked_news_df.iterrows():
                tab_ind=model.get_news_prediction(row["title"],10)
                list_reco.extend(tab_ind[0])
            liste_sans_doublons = list(set(list_reco))
            for i in liste_sans_doublons:
                row_news=news_df.iloc[i]
                insert_stmt = sqlalchemy.text(
                    """INSERT INTO cached_news_dataset (cached_date,user_id,news_id,category_id,title,description,link,image,added_date,source,sub_cat)
                    VALUES (:cached_date,:user_id,:news_id,:category_id,:title,:description,:link,:image,:added_date,:source,:sub_cat)""",
                )
                db_conn.execute(insert_stmt, parameters={"cached_date":cached_date,"user_id":self.user_id, "news_id": row_news['news_id'],"category_id": row_news['category_id'], "title": row_news['title'], "description": row_news['description'],"link":row_news['link'],"image":row_news['image'],"added_date":row_news['added_date'],"source":row_news['source'],"sub_cat":row_news['sub_cat']})
            db_conn.commit()

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



    #Il faudra utiliser la fonction de Mathieu
    def db_to_dataframe_cache(self,nb_rows=20000):
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
            result = self.execute_query_with_df_as_result(query,params)
        else:
            result = self.execute_query_with_df_as_result(query)
        return result


# Code de test de la méthode GO
if __name__ == "__main__":
    # Création d'une instance de la classe TOTO
    cache_test = Cache(2)

    # Appel de la méthode GO pour tester
    #cache_test.clear_all_caches()

    #
   # cache_test.create_one_user_cache(CATEGORIES_ID)
    #df=cache_test.db_to_dataframe_cache(20000)

    #cache_test.remove_one_news_from_cache(129402)

    #cache_test.check_valid_cache(20,CATEGORIES_ID)
    cache_test.get_one_news_for_evaluation(2)
