import sqlite3
import pandas as pd
from database import get_db_connection

# Load the merged and cleaned dataset
movies_df = pd.read_csv('data/cleaned_merged_tmdb_5000_movies.csv')
credits_df = pd.read_csv('data/cleaned_tmdb_5000_credits.csv')

def insert_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insert data into movies table
    for _, row in movies_df.iterrows():
        cur.execute('''
            INSERT INTO movies (id, title, budget, genres, homepage, overview, release_date, revenue, runtime, spoken_languages, tagline, vote_average, vote_count, status, popularity, poster_path, backdrop_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['id'], row['title'], row['budget'], row['genres'], row['homepage'], row['overview'], row['release_date'], row['revenue'], row['runtime'], row['spoken_languages'], row['tagline'], row['vote_average'], row['vote_count'], row['status'], row['popularity'], row['POSTER_PATH'], row['BACKDROP_PATH']))
    
    # Insert data into credits table
    for _, row in credits_df.iterrows():
        cur.execute('''
            INSERT INTO credits (movie_id, title, cast, crew)
            VALUES (?, ?, ?, ?)
        ''', (row['movie_id'], row['title'], row['cast'], row['crew']))
    
    conn.commit()
    conn.close()

# Insert data into the database
insert_data()
