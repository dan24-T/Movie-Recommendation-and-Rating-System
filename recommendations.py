# recommendation.py

import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def get_recommendations(movie_id, db_path='database.db'):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Fetch all movies
    cur.execute("SELECT id, title, genres, overview, backdrop_path FROM movies")
    movies = cur.fetchall()
    conn.close()

    # Convert the movies into a DataFrame
    df_movies = pd.DataFrame(movies, columns=['id', 'title', 'genres', 'overview', 'backdrop_path'])

    # Fill any NaN values in 'genres' and 'overview' columns with empty strings
    df_movies['genres'] = df_movies['genres'].fillna('')
    df_movies['overview'] = df_movies['overview'].fillna('')

    # Combine genres and overview into a single string for TF-IDF
    df_movies['combined_features'] = df_movies['genres'] + " " + df_movies['overview']

    # Initialize the TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_movies['combined_features'])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Get the index of the searched
    idx = df_movies.index[df_movies['id'] == movie_id].tolist()[0]

    # Get the pairwise similarity scores of all movies with the searched movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices of the most similar movies (excluding the searched movie itself)
    movie_indices = [i[0] for i in sim_scores if i[0] != idx]

    # Return the top 10 most similar movies
    recommended_movies = df_movies.iloc[movie_indices][:10]

    return recommended_movies[['id', 'title', 'backdrop_path', 'overview']].to_dict('records')
