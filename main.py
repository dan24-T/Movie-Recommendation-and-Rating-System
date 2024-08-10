from flask import Flask, redirect, url_for, session, flash, render_template
import os
import sqlite3
import json
import pandas as pd

# Import Blueprints
from auth import auth
from admin import admin
from studio import studio_bp
from database import init_db

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(studio_bp)

init_db()

@app.route('/')
def index():
    """
    Redirect to the appropriate page based on user session.
    """
    if 'username' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin.admin_home'))
        return redirect(url_for('home'))
    return redirect(url_for('auth.login'))

@app.route('/home/')
def home():
    """
    Home route for users. Displays user details and sections for different movie categories.
    """
    if 'username' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    # Connect to the database
    conn = sqlite3.connect('database.db')

    # Fetch user details
    cur = conn.cursor()
    cur.execute("SELECT username, first_name, last_name FROM users WHERE username = ?", (session['username'],))
    user = cur.fetchone()

    # Load movies into a DataFrame
    movies_df = pd.read_sql_query("SELECT * FROM movies", conn)

    # Filter top rated, action, animation, and comedy movies
    top_rated = movies_df.sort_values(by='vote_average', ascending=False).head(5)
    action_movies = movies_df[movies_df['genres'].str.contains('Action')].head(5)
    animation_movies = movies_df[movies_df['genres'].str.contains('Animation')].head(5)
    comedy_movies = movies_df[movies_df['genres'].str.contains('Comedy')].head(5)

    conn.close()

    return render_template(
        'home.html', 
        user={'username': user[0], 'first_name': user[1], 'last_name': user[2]},
        top_rated=top_rated,
        action_movies=action_movies,
        animation_movies=animation_movies,
        comedy_movies=comedy_movies
    )

@app.route('/movie/<int:movie_id>/')
def movie_details(movie_id):
    """
    Route to display the details of a specific movie.
    """
    conn = sqlite3.connect('database.db')

    # Fetch movie details by ID
    cur = conn.cursor()
    cur.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cur.fetchone()

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('home'))

    # Convert the fetched data to a dictionary
    movie_details = {
        'id': movie[0],
        'title': movie[1],
        'overview': movie[2],
        'vote_average': movie[3],
        'genres': movie[4],  # Ensure this is a string
        'release_date': movie[5],
        'backdrop_path': movie[16],  # Assuming you have a backdrop_path column
    }

    # Debugging output to check the movie details
    print("Movie Details:")
    print(movie_details)

    # Check if genres is already a list; if not, try to evaluate it
    if isinstance(movie_details['genres'], str):
        try:
            movie_details['genres'] = eval(movie_details['genres'])
        except (SyntaxError, NameError):
            flash('Error parsing genres.', 'error')
            movie_details['genres'] = []
    elif not isinstance(movie_details['genres'], list):
        # If it's not a string or list, log the error
        flash('Unexpected genres format.', 'error')
        movie_details['genres'] = []

    conn.close()

    return render_template('movie_details.html', movie=movie_details)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
