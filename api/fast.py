import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ml_logic.data import get_random_news, save_feedback
from ml_logic.params import USER_ID, CATEGORIES_ID


app = FastAPI()
#app.state.model =load_model()

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
    """
    Diplay a news (a prediction) that the user is supposed to like.
    """
    pass


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
