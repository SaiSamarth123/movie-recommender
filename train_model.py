import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle

# Load movie data
df = pd.read_csv("model/movies.csv")

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["description"])

# Cosine Similarity
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Save everything
with open("model/recommender.pkl", "wb") as f:
    pickle.dump((df, cosine_sim), f)

print("Model Saved ✅")
