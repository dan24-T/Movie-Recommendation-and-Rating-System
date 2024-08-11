import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def load_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('database.db')

    # Load data from the movies and credits tables
    movies_df = pd.read_sql_query("SELECT id, title, overview, genres FROM movies", conn)
    credits_df = pd.read_sql_query("SELECT movie_id, cast, crew FROM credits", conn)

    conn.close()
    
    return movies_df, credits_df

def combine_features(movies_df, credits_df):
    # Merge the movies and credits dataframes on the movie ID
    combined_df = pd.merge(movies_df, credits_df, left_on='id', right_on='movie_id')

    # Combine the relevant features into a single string
    combined_df['combined_features'] = combined_df.apply(lambda x: f"{x['overview']} {x['genres']} {x['cast']} {x['crew']}", axis=1)

    return combined_df

def generate_recommendations(movie_title, combined_df):
    # Create a TF-IDF Vectorizer object
    tfidf = TfidfVectorizer(stop_words='english')

    # Fit and transform the combined features
    tfidf_matrix = tfidf.fit_transform(combined_df['combined_features'])

    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Get the index of the movie that matches the title
    idx = combined_df[combined_df['title'].str.lower() == movie_title.lower()].index[0]

    # Get the pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices of the most similar movies
    movie_indices = [i[0] for i in sim_scores[1:11]]  # Exclude the first match (itself)

    # Return the top 10 most similar movies
    return combined_df.iloc[movie_indices][['title', 'genres']].to_dict(orient='records')

def get_recommendations_for_movie(movie_title):
    # Load the data
    movies_df, credits_df = load_data()

    # Combine the features
    combined_df = combine_features(movies_df, credits_df)

    # Generate recommendations
    recommendations = generate_recommendations(movie_title, combined_df)

    return recommendations