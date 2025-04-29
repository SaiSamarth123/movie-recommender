from flask import Flask, request, render_template
import pickle
import os
import requests
from dotenv import load_dotenv


load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


app = Flask(__name__)
print("[INFO] Flask app loaded")  # boot confirmation


try:
    with open("model/recommender.pkl", "rb") as f:
        df, cosine_sim = pickle.load(f)
    print("[INFO] Recommender model loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load recommender model: {e}")
    df = None
    cosine_sim = None


def recommend_by_genre(title, api_key):
    print(f"[INFO] Searching TMDB for '{title}'...")

    search_url = (
        f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    )
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        results = response.json().get("results", [])
    except Exception as e:
        print(f"[ERROR] TMDB search failed: {e}")
        return ["Error contacting TMDB."]

    if not results:
        return ["Movie not found on TMDB. Try another."]

    movie = results[0]
    genre_ids = movie.get("genre_ids", [])
    if not genre_ids:
        return ["Could not find genre info. Try another."]

    genre_str = ",".join(map(str, genre_ids))
    discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_str}&sort_by=popularity.desc"

    try:
        discover_response = requests.get(discover_url)
        discover_response.raise_for_status()
        similar_movies = discover_response.json().get("results", [])[:5]
        return [m["title"] for m in similar_movies]
    except Exception as e:
        print(f"[ERROR] TMDB genre fetch failed: {e}")
        return ["Failed to fetch similar movies."]


def recommend(title):
    if not df or not cosine_sim:
        return ["Model not available. Try again later."]

    title = title.lower()
    idx = df[df["title"].str.lower() == title].index

    if len(idx) == 0:
        return recommend_by_genre(title, TMDB_API_KEY)

    idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    movie_indices = [i[0] for i in sim_scores]
    return df["title"].iloc[movie_indices].tolist()


@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    if request.method == "POST":
        title = request.form.get("title")
        if title:
            recommendations = recommend(title)
    return render_template("index.html", recommendations=recommendations)


# ✅ Railway-compatible run config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
