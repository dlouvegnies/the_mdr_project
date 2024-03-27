from sentence_transformers import SentenceTransformer

def encode_sentence(keywords:str):
    model = SentenceTransformer("dangvantuan/sentence-camembert-base")
    keywords_embedded = model.encode(keywords)
    return keywords_embedded
