import pandas as pd
import numpy as np
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from google.cloud import bigquery
from google.oauth2 import service_account

from ml_logic.data import get_random_news, save_feedback, db_to_dataframe, get_last_news_liked
from ml_logic.params import USER_ID, CATEGORIES_ID, CREDENTIAL_PATH
from ml_logic.model import Model

def get_bigquery_client():
    # Charger les informations d'identification depuis le fichier de clé JSON
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    # Initialiser et retourner le client BigQuery
    return bigquery.Client(credentials=credentials, project=credentials.project_id)

app = FastAPI()


"""
To launch the server :
uvicorn api.fast:app --reload
"""

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/get_one_news_to_learn")
def get_one_news_to_learn(user_id:int):
    """
    Diplay a news to know if the user like it or not, in order to learn his tastes
    """
    news = get_random_news(user_id=USER_ID, categories=CATEGORIES_ID, nb_news=1).to_dict()
    return news



@app.post("/save_one_learning")
def save_one_learning(feedback:dict):
    """
    Save, for the user, his taste for this news
    value = 0 or 1
    """
    result = save_feedback(feedback)
    if result:
        return {"message": "Feedback saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save feedback")


@app.get("/get_one_news_to_evaluate")
def get_one_news_to_evaluate(user_id:int):
    #bq_client: bigquery.Client = Depends(get_bigquery_client)
    """
    Diplay a news (a prediction) that the user is supposed to like.
    """
    # Retrieve BQ data in Dataframe and cleaning it
    data_filename = "raw_data/data_for_model.csv"

    if os.path.exists(data_filename):
        news_df = pd.read_csv(data_filename)
        news_df.replace(np.nan, None, inplace=True)
    else:
        news_df = db_to_dataframe(nb_rows=200000)
        news_df = news_df.drop_duplicates()
        news_df.replace(np.nan, None, inplace=True)
        news_df.to_csv(data_filename, index=False)

    model = Model(news_df)

    last_news_liked = get_last_news_liked(user_id)
    neigh_ind = model.get_news_prediction(last_news_liked.title[0], 10)
    neigh_news = news_df.iloc[neigh_ind[0]].iloc[1, :].to_frame().to_dict() # Retrieve the seconde near news
    print('--------------------')
    print({'news': next(iter(neigh_news.values()))})
    print('--------------------')
    return neigh_news



@app.get("/save_one_evaluation")
def save_one_evaluation(feedback:dict):
    """
    Save, for the user, if the prediction to like this news is right or wrong
    value = 0 or 1
    """
    result = save_feedback(feedback)
    if result:
        return {"message": "Feedback saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save feedback")


@app.get("/")
def root():
    # YOUR CODE HERE
    return {'greeting': 'Hello'}
