from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import pymysql
from ml_logic.params import DB_SERVER,USER_DB,PASSWORD_DB,DB_NAME,CACHE_VALIDATION_DURATION
import ml_logic.data_mysql as dm
from sqlalchemy.exc import SQLAlchemyError

class Category:

    def __init__(self,user_id):
        self.user_id = user_id
        self.connector = Connector()

        # function to return the database connection
    def getconn(self) -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = self.connector.connect(DB_SERVER,"pymysql",user=USER_DB,password=PASSWORD_DB,db=DB_NAME,charset='utf8mb4',collation='utf8mb4_unicode_ci')
        return conn

    """
    Return the list all categories
    """
    def get_categories_dict(self):

        sql_query = f"SELECT * FROM category_dataset order by cat_name"
        df=dm.execute_query_with_df_as_result_no_params(sql_query)

        return df.to_dict()

    """
    Return the dictionnaire of the user's categorie
    """
    def get_user_categories(self):

        sql_query = f"SELECT c.category_id, c.cat_name FROM category_user_dataset cu, category_dataset c where cu.user_id = {self.user_id} and c.category_id=cu.category_id order by c.cat_name"
        df=dm.execute_query_with_df_as_result(sql_query,params={})
        df= df.set_index('category_id')
        dictionnaire = df.to_dict()["cat_name"]
        dictionnaire = {k: v.capitalize() for k, v in dictionnaire.items()}
        #print(dictionnaire)
        return dictionnaire

    """
    Return the list of the user's categories ids
    """
    def get_user_categories_ids(self):

        sql_query = f"SELECT category_id FROM category_user_dataset WHERE user_id = {self.user_id}  order by category_id"
        df=dm.execute_query_with_df_as_result(sql_query,params={})
        list_=df["category_id"].tolist()
        return list_



    """
    Return the list of the user's categorie
    """
    def get_user_categories_and_list(self):

        sql_query = f"Select cd.category_id, cd.cat_name ,cud.user_id  from category_dataset cd LEFT JOIN category_user_dataset cud ON cd.category_id = cud.category_id and cud.user_id={self.user_id} order by cd.cat_name"
        df=dm.execute_query_with_df_as_result(sql_query,params={})
        df = df.fillna('')
        print(df)
        return df.to_dict()


    def save_user_category(self,category_id:int,on:bool):

        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)
        db_conn = pool.connect()
        with db_conn:
            try:
                #Need to activate the category
                if on==True:
                    #Delete just in case.
                    sql_query = sqlalchemy.text("""DELETE FROM category_user_dataset WHERE user_id =:user_id and category_id=:category_id""",)
                    db_conn.execute(sql_query, parameters={"user_id":self.user_id,"category_id":category_id})
                    insert_stmt = sqlalchemy.text(
                                """INSERT INTO category_user_dataset (category_id,user_id) VALUES (:category_id,:user_id)""",)
                    db_conn.execute(insert_stmt, parameters={"category_id":category_id,"user_id":self.user_id})
                else:
                    sql_query = sqlalchemy.text("""DELETE FROM category_user_dataset WHERE user_id =:user_id and category_id=:category_id""",)
                    db_conn.execute(sql_query, parameters={"user_id":self.user_id,"category_id":category_id})

                db_conn.commit()
                db_conn.close()
                return True
            except SQLAlchemyError:
                return False



    """
    Save user's categorie
    """
    def save_user_categories(self,category_list=list):

        pool = sqlalchemy.create_engine("mysql+pymysql://",creator=self.getconn)
        db_conn = pool.connect()

        #---1--- DELETE existing categories
        sql_query = sqlalchemy.text("""DELETE FROM category_user_dataset WHERE user_id =:user_id""",)
        db_conn.execute(sql_query, parameters={"user_id":self.user_id})

        #---2--- INSERT NEW CATEGORIE
        with db_conn:
            try:
                for category_id in category_list:
                    insert_stmt = sqlalchemy.text(
                        """INSERT INTO category_user_dataset (category_id,user_id) VALUES (:category_id,:user_id)""",)
                    db_conn.execute(insert_stmt, parameters={"category_id":category_id,"user_id":self.user_id})
                db_conn.commit()
                db_conn.close()
                return True
            except SQLAlchemyError:
                return False





        # function to return the database connection
    def getconn(self) -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = self.connector.connect(DB_SERVER,"pymysql",user=USER_DB,password=PASSWORD_DB,db=DB_NAME,charset='utf8mb4',collation='utf8mb4_unicode_ci')
        return conn



# Code de test de la méthode GO
if __name__ == "__main__":

    cat_obj = Category(3)
    #print(cat_obj.get_categories_dict())
    #print(cat_obj.get_user_categories())
    cat_obj.save_user_categories([1,4,7])
    cat_obj.get_user_categories_ids()
