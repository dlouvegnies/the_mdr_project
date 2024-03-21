
import pandas as pd
import numpy as np
import os

from ml_logic.data import db_to_dataframe, get_last_news_liked
from ml_logic.params import MODEL_NEWS_BATCH_SIZE, CATEGORIES_ID
from ml_logic.model import Model

def get_one_reco_by_last_liked(user_id:int, categories=CATEGORIES_ID):
    # Retrieve BQ data in Dataframe and cleaning it
    data_filename = os.path.join("raw_data", "data_for_model.csv")

    if os.path.exists(data_filename):
        news_df = pd.read_csv(data_filename)
        news_df.replace(np.nan, None, inplace=True)
    else:
        news_df = db_to_dataframe(nb_rows=MODEL_NEWS_BATCH_SIZE)
        news_df = news_df.drop_duplicates()
        news_df.replace(np.nan, None, inplace=True)
        news_df.to_csv(data_filename, index=False)

    model = Model(news_df)

    last_news_liked = get_last_news_liked(user_id, categories) #if last_news_liked.empty SERVER ERROR
    neigh_ind = model.get_news_prediction(last_news_liked.title[0], 10)
    random_news_in_neigh_news = np.random.randint(1,10)
    neigh_news = news_df.iloc[neigh_ind[0]].iloc[random_news_in_neigh_news, :].to_frame().to_dict() # Retrieve the seconde near news
    print('--------------------')
    print({'news': next(iter(neigh_news.values()))})
    print('--------------------')
    return neigh_news
