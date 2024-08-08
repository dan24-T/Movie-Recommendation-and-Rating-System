import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create users table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS studios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            studio_name TEXT NOT NULL,
            studio_country TEXT NOT NULL,
            business_email TEXT NOT NULL,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            verified INTEGER NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create movies table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            budget INTEGER,
            genres TEXT,
            homepage TEXT,
            overview TEXT,
            release_date TEXT,
            revenue INTEGER,
            runtime INTEGER,
            spoken_languages TEXT,
            tagline TEXT,
            vote_average REAL DEFAULT 0,
            vote_count INTEGER DEFAULT 0,
            status TEXT,
            popularity REAL DEFAULT 0,
            poster_path TEXT,
            backdrop_path TEXT,
            studio_id INTEGER,
            FOREIGN KEY (studio_id) REFERENCES studios(id)
        )
    ''')
    
    # Create credits table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            title TEXT NOT NULL,
            cast TEXT,
            crew TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()
