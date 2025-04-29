import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of IMDb Top 250 Movies
url = "https://www.imdb.com/chart/top/"

headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

movies = soup.select("td.titleColumn")
links = [a.attrs.get("href") for a in soup.select("td.titleColumn a")]
descriptions = []

# Scrape description for each movie
for link in links[:100]:  # Only first 100 movies to be fast
    movie_url = f"https://www.imdb.com{link}"
    movie_page = requests.get(movie_url, headers=headers)
    movie_soup = BeautifulSoup(movie_page.text, "html.parser")
    desc = movie_soup.find("span", {"data-testid": "plot-l"})
    if desc:
        descriptions.append(desc.text.strip())
    else:
        descriptions.append("No description available.")

titles = [movie.a.text for movie in movies][:100]

# Save to DataFrame
df = pd.DataFrame({"title": titles, "description": descriptions})

df.to_csv("model/movies.csv", index=False)
print("Scraping Done ✅")
