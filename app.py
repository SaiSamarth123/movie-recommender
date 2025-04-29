from flask import Flask, request, render_template
import pickle
import os

from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Auto-run generate_model.py if model not exists
if not os.path.exists("model/recommender.pkl"):
    print("[INFO] No model found. Auto-generating model...")
    os.system("python3 scripts/generate_model.py")

app = Flask(__name__)

# Load recommender
with open("model/recommender.pkl", "rb") as f:
    df, cosine_sim = pickle.load(f)


def recommend(title):
    title = title.lower()
    idx = df[df["title"].str.lower() == title].index

    if len(idx) == 0:
        # fallback to genre-based recommendation
        return recommend_by_genre(title, TMDB_API_KEY)

    idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]
    return df["title"].iloc[movie_indices].tolist()


import requests


def recommend_by_genre(title, api_key):
    print(f"[INFO] Searching TMDB for '{title}'...")

    # Step 1: Search movie
    search_url = (
        f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    )
    response = requests.get(search_url).json()
    results = response.get("results")

    if not results:
        return ["Movie not found on TMDB. Try another."]

    movie = results[0]
    genre_ids = movie.get("genre_ids", [])

    if not genre_ids:
        return ["Could not find genre info. Try another."]

    genre_str = ",".join(map(str, genre_ids))

    # Step 2: Get similar genre movies
    discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_str}&sort_by=popularity.desc"
    discover_response = requests.get(discover_url).json()

    similar_movies = discover_response.get("results", [])[:5]

    return [m["title"] for m in similar_movies]


@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    if request.method == "POST":
        title = request.form.get("title")
        recommendations = recommend(title)
    return render_template("index.html", recommendations=recommendations)


if __name__ == "__main__":
    app.run(debug=True)
