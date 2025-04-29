import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def fetch_tmdb_movies(api_key, num_movies=50):
    print("[INFO] Fetching movies from TMDB API...")
    movies = []
    page = 1

    while len(movies) < num_movies:
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page={page}"
        response = requests.get(url)
        data = response.json()

        for movie in data.get("results", []):
            title = movie.get("title")
            description = movie.get("overview", "").strip()

            if title and description:  # Only add if both exist
                movies.append({"title": title, "description": description})

            if len(movies) >= num_movies:
                break

        page += 1

    if not movies:
        raise ValueError("[ERROR] No valid movies fetched from TMDB!")

    df = pd.DataFrame(movies)
    os.makedirs("model", exist_ok=True)
    df.to_csv("model/movies.csv", index=False)
    print(f"[INFO] Scraped {len(df)} movies from TMDB ✅")
    return df


def train_model(df):
    print("[INFO] Training TF-IDF model...")
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(df["description"])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    with open("model/recommender.pkl", "wb") as f:
        pickle.dump((df, cosine_sim), f)

    print("[INFO] Model Saved ✅")


def main():
    if os.path.exists("model/recommender.pkl"):
        print("[INFO] Model already exists. Skipping scraping and training ✅")
    else:
        print("[INFO] No model found. Running full data fetch + training...")
        df = fetch_tmdb_movies(TMDB_API_KEY)
        train_model(df)


if __name__ == "__main__":
    main()
