from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import pickle
import os
import string
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os


class Model:

    def __init__(self,X_df, column_name="title",max_size=25000):
        # Assign an attribute ".data" to all new instances of Order
        max_size=20000
        self.vectorizer_filename = os.path.join("models","best_vectorizer.pkl")
        self.model_filename = os.path.join("models","best_model.pkl")
        self.vectorizer = None
        self.model = self.load_model(X_df, column_name,max_size)

        print("init done")


    def load_model(self,X_df=None,column_name="title",max_size=25000):
        if os.path.exists(self.model_filename):
            with open(self.model_filename, 'rb') as file:
                self.model = pickle.load(file)
        else:
            self.create_model(X_df, column_name,max_size)

        if os.path.exists(self.vectorizer_filename):
            with open(self.vectorizer_filename, 'rb') as file:
                self.vectorizer = pickle.load(file)

        return self.model


    def save_model(self):
        with open(self.vectorizer_filename, 'wb') as file:
            pickle.dump(self.vectorizer, file)

        with open(self.model_filename, 'wb') as file:
            pickle.dump(self.model, file)


    def create_model(self,X_df, column_name="title",max_size=25000):

        size = X_df.shape[0]
        train_size = max_size
        if size<max_size :
            train_size = size

        #Step ONE : Vectorize
        tf_idf_vectorizer = TfidfVectorizer(max_features=500)
        print("TfidfVectorizer")
        test_list = []
        for i in range(0,train_size):
            titre = X_df.iloc[i][column_name]
            titre = np.str_(titre)
            test_list.append(titre)

        tf_idf_vectorizer.fit(test_list)

        weighted_words = pd.DataFrame(tf_idf_vectorizer.transform(test_list).toarray(),columns = tf_idf_vectorizer.get_feature_names_out())
        print("fin TfidfVectorizer")
        #Step TWO : FIT the MODEL
        weighted_words_list = weighted_words.values.tolist()
        model = NearestNeighbors(n_neighbors=1)
        model.fit(weighted_words_list)
        print("fin fit")

        self.model = model
        self.vectorizer = tf_idf_vectorizer
        self.save_model()


    def get_news_prediction(self,titre_source,nb_news=10):
        titre_source = np.str_(titre_source)
        weighted_words = pd.DataFrame(self.vectorizer.transform([titre_source]).toarray(),columns = self.vectorizer.get_feature_names_out())
        weighted_words_list=weighted_words.values.tolist()
        neigh_dist, news_indexs = self.model.kneighbors(weighted_words_list,nb_news)
        return news_indexs


    #To be used for V2
    def cleaning(self,sentence):
        # Basic cleaning
        sentence = sentence.strip() ## remove whitespaces
        sentence = sentence.lower() ## lowercase
        sentence = ''.join(char for char in sentence if not char.isdigit()) ## remove numbers
        # Advanced cleaning
        for punctuation in string.punctuation:
            sentence = sentence.replace(punctuation, '') ## remove punctuation
            tokenized_sentence = word_tokenize(sentence) ## tokenize
            stop_words = set(stopwords.words('french')) ## define stopwords

        ## remove stopwords
        tokenized_sentence_cleaned = [w for w in tokenized_sentence if not w in stop_words]
        lemmatized = [WordNetLemmatizer().lemmatize(word, pos = "v") for word in tokenized_sentence_cleaned]
        cleaned_sentence = ' '.join(word for word in lemmatized)
        return cleaned_sentence
