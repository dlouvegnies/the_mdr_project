from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from google.cloud import bigquery
from google.oauth2 import service_account

from ml_logic.data_mysql import get_random_news, save_feedback, db_to_dataframe, reset_review_dataset
from ml_logic.params import  CREDENTIAL_PATH, DAY, MONTH, YEAR
from ml_logic.recommendation import get_top_similar_news #get_one_reco_by_last_liked, get_one_reco_by_last_liked_with_bert
from ml_logic.user_mysql import create_user, connect_user
from ml_logic.cache import Cache
from ml_logic.cache_bert import Cache_Bert

from datetime import datetime

from ml_logic.category import Category
from ml_logic.search import encode_sentence

def get_bigquery_client():
    # Charger les informations d'identification depuis le fichier de clé JSON
    credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PATH)
    # Initialiser et retourner le client BigQuery
    return bigquery.Client(credentials=credentials, project=credentials.project_id)

app = FastAPI()
news_df = db_to_dataframe(date=datetime(YEAR, MONTH, DAY))

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
    news = get_random_news(user_id=user_id, nb_news=1)
    news.drop(columns=['embedding'], inplace=True) # May be, make precise request to evitate retrieving data for nothing
    return news.to_dict()



@app.post("/save_one_learning")
def save_one_learning(feedback:dict):
    """
    Save, for the user, his taste for this news
    value = 0 or 1
    """
    result = save_feedback(feedback)
    if result:
        return {"message": "Feedback saved successfully",
                "status_code": 200}
    else:
        raise HTTPException(status_code=500, detail="Failed to save feedback")


@app.get("/get_one_news_to_evaluate")
def get_one_news_to_evaluate(user_id:int, categories:list[int]=Query(None)):
    #bq_client: bigquery.Client = Depends(get_bigquery_client)
    """
    Diplay a news (a prediction) that the user is supposed to like.
    """
    # if categories is None:
    #     reco_by_last_liked = get_one_reco_by_last_liked(user_id)
    # else:
    #     reco_by_last_liked = get_one_reco_by_last_liked(user_id, categories=categories)

    cache = Cache(user_id)
    return cache.get_one_news_for_evaluation()
    #return reco_by_last_liked


@app.get("/get_one_reco_by_bert")
def get_one_reco_by_bert(user_id:int, method, categories:list[int]=Query(None)):
    #bq_client: bigquery.Client = Depends(get_bigquery_client)
    """
    Diplay a news (a prediction) that the user is supposed to like with bert model.
    """
    # if categories is None: #Request.app.state.news_of_the_day,
    #     bert_reco = get_one_reco_by_last_liked_with_bert(news_df,
    #                                                      user_id=user_id,
    #                                                      method=method)
    # else:
    #     bert_reco = get_one_reco_by_last_liked_with_bert(news_df,
    #                                                      user_id=user_id,
    #                                                      method=method,
    #                                                      categories=categories)
    #return bert_reco
    cache_bert = Cache_Bert(user_id)
    return cache_bert.get_one_news_for_evaluation(news_df, method=method)



@app.post("/save_one_evaluation")
def save_one_evaluation(feedback:dict):
    """
    Save, for the user, if the prediction to like this news is right or wrong
    value = 0 or 1
    """
    result = save_feedback(feedback)
    if result:
        return {"message": "Feedback saved successfully",
                "status_code": 200}
    else:
        raise HTTPException(status_code=500, detail="Failed to save feedback")


@app.post("/signup")
def signup(user:dict):
    # Logique pour vérifier si l'utilisateur existe déjà, sinon ajouter à la base de données
    result = create_user(user)
    match result:
        case -1:
            raise HTTPException(status_code=401, detail='This user already exist')
        case 0:
            raise HTTPException(status_code=401, detail='Account creation failed')
        case 1:
            return {"message": "User signed up successfully",
                    "status_code": 200}


@app.post("/login")
def login(user:dict):
    result = connect_user(user)
    if not result.empty:

        return {"message": "Login successful",
                "status_code": 200,
                "result": result.to_dict()}
    else:
        raise HTTPException(status_code=401, detail="This account is not exist")



@app.get("/clear_one_user_cache")
def clear_one_user_cache(user_id:int):
    """
    Clear the cache of one user
    """
    cache = Cache(user_id)
    cache.clear_user_cache()
    return {"message": "Cache clear",
            "status_code": 200}


@app.get("/get_categories_dict")
def get_categories_dict():
    """
    Get the dict of all categories
    """
    cat_obj = Category(0)
    return cat_obj.get_categories_dict()


@app.get("/get_one_user_category")
def get_one_user_category(user_id:int):
    """

    """
    cat_obj = Category(user_id)
    #return cat_obj.get_user_categories()
    return cat_obj.get_user_categories_and_list()


@app.post("/save_user_categories")
def save_user_categories(user_id=int,category_list=list):
    """

    """
    category_list = set(category_list.split(','))
    print(f"--------Category LIST= {category_list}")
    cat_obj = Category(user_id)
    result=cat_obj.save_user_categories(category_list)
    if result:
        return {"message": "User categories saved successfully",
                    "status_code": 200}
    else:
        raise HTTPException(status_code=500, detail="Failed to save User categories")


@app.get("/reset")
def reset_user_profile(user_id:int):
    """
    Reset profile information
    """
    reset_review_dataset(user_id)
    return {"message": "User profile deleted successfully",
                    "status_code": 200}

@app.post("/save_user_category")
def save_user_category(user_id=int,category_id=int,on=int):
    """

    """
    if int(on)==1:
        on=True
    else:
        on=False
    cat_obj = Category(user_id)
    result=cat_obj.save_user_category(category_id,on)
    if result:
        return {"message": "User categories saved successfully",
                    "status_code": 200}
    else:
        raise HTTPException(status_code=500, detail="Failed to save User categories")

@app.post("/search")
def get_news_from_keywords(search:dict):
    keywords = search['keywords']
    keywords_embedded = encode_sentence(keywords)
    recommendation_df = get_top_similar_news(keywords_embedded, news_df, num_recommendations=10)
    recommendation_df.drop(columns=['embedding', 'news_id', 'category_id', 'sub_cat', 'added_date', 'image'], inplace=True)

    if not recommendation_df.empty:
        return {"message": "Feedback saved successfully",
                "status_code": 200,
                "result": recommendation_df.to_dict()}
    else:
        raise HTTPException(status_code=500, detail="Failed to save feedback")



@app.get("/")
def root():
    # YOUR CODE HERE
    return {'greeting': 'Hello'}
