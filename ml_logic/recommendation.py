
import pandas as pd
import numpy as np
import os
import ast


from ml_logic.data_mysql import db_to_dataframe, get_last_news_liked
from ml_logic.params import MODEL_NEWS_BATCH_SIZE
from ml_logic.model import Model
from ml_logic.category import Category

from sklearn.metrics.pairwise import cosine_similarity

from datetime import datetime

################# TFIDF #################

def get_one_reco_by_last_liked(user_id:int, categories=[]):
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

    if categories==[]:
        cat_obj = Category(user_id=user_id)
        categories=cat_obj.get_user_categories_ids()

    last_news_liked = get_last_news_liked(user_id, categories) #if last_news_liked.empty SERVER ERROR
    neigh_ind = model.get_news_prediction(last_news_liked.title[0], 10)
    random_news_in_neigh_news = np.random.randint(1,10)
    neigh_news = news_df.iloc[neigh_ind[0]].iloc[random_news_in_neigh_news, :].to_frame().to_dict() # Retrieve the seconde near news
    print('--------------------')
    print({'news': next(iter(neigh_news.values()))})
    print('--------------------')
    return neigh_news


################# BERT #################
def get_one_reco_by_last_liked_with_bert(news_df, user_id:int, categories=[], method='cosine', date=datetime(2024, 3, 18)):

    data_filename = os.path.join("raw_data", f"data_for_bert_{date.strftime('%Y-%m-%d')}.csv")

    # if os.path.exists(data_filename):
    #     news_df = pd.read_csv(data_filename, converters={"embedding": convert_embedding})
    #     news_df.replace(np.nan, None, inplace=True)
    # else:
    #     news_df = db_to_dataframe(date=date, nb_rows=1000)
    #     news_df.replace(np.nan, None, inplace=True)
    #     news_df.to_csv(data_filename, index=False)

    if categories==[]:
        cat_obj = Category(user_id)
        categories=cat_obj.get_user_categories_ids()

    last_news_liked = get_last_news_liked(user_id, categories) #if last_news_liked.empty SERVER ERROR
    embedding = last_news_liked['embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float64).tolist()).values[0]
    recommended_news = get_top_similar_news(np.array(embedding), news_df, 1, method=method)
    recommended_news.drop(columns=['embedding'], inplace=True)
    return recommended_news.to_dict()

def convert_embedding(embedding_str):
    embedding_list = ast.literal_eval(embedding_str)
    return embedding_list

def get_top_similar_news(news_embedded, news_df, num_recommendations, method='cosine'):
    # Map method to associated function
    similarity_functions = {
        'cosine': compute_cosine_similarity,
        'euclidean': compute_euclidean_distance,
        'manhattan': compute_manhattan_distance,
        'jaccard': compute_jaccard_similarity
    }
    if method not in similarity_functions:
        raise ValueError("Invalid method. Valid options are 'cosine', 'euclidean', 'manhattan', and 'jaccard'.")

    # Compute the similaritues
    similarity_function = similarity_functions[method]
    similarities = []
    for idx, row in news_df.iterrows():
        similarity = similarity_function(news_embedded, row['embedding'])
        similarities.append((idx, similarity))

    # Retrieve the best news
    if method in ['cosine', 'jaccard']:
        sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    else:
        sorted_similarities = sorted(similarities, key=lambda x: x[1])

    top_similar_news_indices = [idx for idx, _ in sorted_similarities[:num_recommendations]]
    top_similar_news = news_df.loc[top_similar_news_indices]

    return top_similar_news

def compute_cosine_similarity(first_embedding, second_embedding):
    dot_product = np.dot(first_embedding, second_embedding)

    norm_first_emb = np.linalg.norm(first_embedding)
    norm_second_emb = np.linalg.norm(second_embedding)

    cosine_sim = dot_product / (norm_first_emb * norm_second_emb)
    return cosine_sim

def compute_jaccard_similarity(first_embedding, second_embedding):
    intersection = np.logical_and(first_embedding, second_embedding).sum()
    union = np.logical_or(first_embedding, second_embedding).sum()
    jac_sim = intersection / union if union != 0 else 0
    return jac_sim

def compute_euclidean_distance(first_embedding, second_embedding):
    return np.linalg.norm(first_embedding - second_embedding)

def compute_manhattan_distance(first_embedding, second_embedding):
    return np.sum(np.abs(first_embedding - second_embedding))
