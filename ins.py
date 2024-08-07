import sqlite3
import pandas as pd

def get_db_connection():
    """
    Get a connection to the SQLite database.
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """
    Create the necessary tables in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Create movies table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            budget INTEGER,
            genres TEXT,
            homepage TEXT,
            keywords TEXT,
            original_language TEXT,
            original_title TEXT,
            overview TEXT,
            popularity REAL,
            production_companies TEXT,
            production_countries TEXT,
            release_date TEXT,
            revenue INTEGER,
            runtime REAL,
            spoken_languages TEXT,
            status TEXT,
            tagline TEXT,
            title TEXT,
            vote_average REAL,
            vote_count INTEGER
        )
    ''')

    # Create credits table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS credits (
            movie_id INTEGER PRIMARY KEY,
            title TEXT,
            cast TEXT,
            crew TEXT
        )
    ''')

    conn.commit()
    conn.close()

def insert_data():
    """
    Insert data from CSV files into the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Load CSV data
    movies_df = pd.read_csv('data/tmdb_5000_movies.csv')
    credits_df = pd.read_csv('data/tmdb_5000_credits.csv')

    # Insert movies data
    for index, row in movies_df.iterrows():
        cur.execute('''
            INSERT INTO movies (id, budget, genres, homepage, keywords, original_language, original_title, overview, popularity, 
                                production_companies, production_countries, release_date, revenue, runtime, spoken_languages, status, 
                                tagline, title, vote_average, vote_count) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['id'], row['budget'], row['genres'], row['homepage'], row['keywords'], row['original_language'], row['original_title'],
              row['overview'], row['popularity'], row['production_companies'], row['production_countries'], row['release_date'],
              row['revenue'], row['runtime'], row['spoken_languages'], row['status'], row['tagline'], row['title'],
              row['vote_average'], row['vote_count']))

    # Insert credits data
    for index, row in credits_df.iterrows():
        cur.execute('''
            INSERT INTO credits (movie_id, title, cast, crew) 
            VALUES (?, ?, ?, ?)
        ''', (row['movie_id'], row['title'], row['cast'], row['crew']))

    conn.commit()
    conn.close()

# Create tables
create_tables()

# Insert data
insert_data()
