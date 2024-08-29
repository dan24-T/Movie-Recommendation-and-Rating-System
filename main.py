from flask import Flask, redirect, url_for, session, flash, render_template, request, jsonify
import sqlite3
import os
import pandas as pd
import json

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
from recommendations import get_recommendations  # Import the recommendation function

init_db()

@app.route('/')
def index():
    # Redirect to the appropriate page based on user session.
    if 'username' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin.admin_home'))
        return redirect(url_for('home'))
    return redirect(url_for('auth.login'))

@app.route('/about')
def about():
    """
    Render the about page.
    """
    return render_template('about.html')

@app.route('/home/')
def home():
    # Home route for users. Displays sections for different movie categories.
    if 'username' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Fetch user details
    cur.execute("SELECT username, first_name, last_name FROM users WHERE username = ?", (session['username'],))
    user = cur.fetchone()

    # Load movies into a DataFrame
    movies_df = pd.read_sql_query("SELECT * FROM movies", conn)

    # Filter top-rated, action, animation, and comedy movies
    top_rated = movies_df.sort_values(by='vote_average', ascending=False).head(10)
    action_movies = movies_df[movies_df['genres'].str.contains('Action')].head(10)
    animation_movies = movies_df[movies_df['genres'].str.contains('Animation')].head(10)
    comedy_movies = movies_df[movies_df['genres'].str.contains('Comedy')].head(10)

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
    conn = sqlite3.connect('database.db')

    # Fetch movie details by ID
    cur = conn.cursor()
    cur.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cur.fetchone()

    if not movie:
        flash('Movie not found.', 'error')
        return redirect(url_for('home'))

    movie_details = {
        'id': movie[0],
        'title': movie[1],
        'overview': movie[2],
        'vote_average': movie[11],
        'genres': movie[3],
        'release_date': movie[6],
        'backdrop_path': movie[16],
    }

    if isinstance(movie_details['genres'], str):
        try:
            movie_details['genres'] = eval(movie_details['genres'])
        except (SyntaxError, NameError):
            flash('Error parsing genres.', 'error')
            movie_details['genres'] = []
    elif not isinstance(movie_details['genres'], list):
        flash('Unexpected genres format.', 'error')
        movie_details['genres'] = []

    # Fetch reviews for this movie, ordered by upvotes descending
    cur.execute("""
        SELECT r.id, r.rating, r.review_text, r.upvotes, r.downvotes, u.username,
               (SELECT vote_type FROM review_votes WHERE user_id = ? AND review_id = r.id) as user_vote
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.movie_id = ?
        ORDER BY r.upvotes DESC
    """, (session.get('user_id'), movie_id))
    reviews = cur.fetchall()

    conn.close()

    return render_template('movie_details.html', movie=movie_details, reviews=reviews)

@app.route('/movie/<int:movie_id>/add_review', methods=['POST'])
def add_review(movie_id):
    """
    Route to add a review for a movie.
    """
    if 'username' not in session:
        flash('You need to be logged in to add a review.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    rating = request.form.get('rating')
    review_text = request.form.get('review_text')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Check if the user has already reviewed this movie
    cur.execute("SELECT id FROM reviews WHERE user_id = ? AND movie_id = ?", (user_id, movie_id))
    existing_review = cur.fetchone()

    if existing_review:
        flash('You have already reviewed this movie.', 'error')
    else:
        cur.execute("INSERT INTO reviews (movie_id, user_id, rating, review_text) VALUES (?, ?, ?, ?)",
                    (movie_id, user_id, rating, review_text))

        # Update movie's vote_count and vote_average
        cur.execute("UPDATE movies SET vote_count = vote_count + 1 WHERE id = ?", (movie_id,))
        cur.execute("SELECT AVG(rating) FROM reviews WHERE movie_id = ?", (movie_id,))
        new_vote_average = cur.fetchone()[0]
        cur.execute("UPDATE movies SET vote_average = ? WHERE id = ?", (new_vote_average, movie_id))

        conn.commit()
        flash('Review added successfully.', 'success')

    conn.close()
    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/movie/<int:movie_id>/edit_review', methods=['POST'])
def edit_review(movie_id):
    """
    Route to edit an existing review for a movie.
    """
    if 'username' not in session:
        flash('You need to be logged in to edit a review.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    rating = request.form.get('rating')
    review_text = request.form.get('review_text')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        UPDATE reviews SET rating = ?, review_text = ?
        WHERE user_id = ? AND movie_id = ?
    """, (rating, review_text, user_id, movie_id))

    # Update movie's vote_average
    cur.execute("SELECT AVG(rating) FROM reviews WHERE movie_id = ?", (movie_id,))
    new_vote_average = cur.fetchone()[0]
    cur.execute("UPDATE movies SET vote_average = ? WHERE id = ?", (new_vote_average, movie_id))

    conn.commit()
    conn.close()

    flash('Review updated successfully.', 'success')
    return redirect(url_for('movie_details', movie_id=movie_id))

@app.route('/movie/<int:movie_id>/upvote/<int:review_id>', methods=['POST'])
def upvote_review(movie_id, review_id):
    if 'username' not in session:
        flash('You need to be logged in to upvote.', 'error')
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Get the user's ID
    cur.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    # Check if the user has already voted on this review
    cur.execute("SELECT vote_type FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
    vote = cur.fetchone()

    if vote:
        if vote[0] == 'upvote':
            # The user already upvoted, so undo the upvote
            cur.execute("UPDATE reviews SET upvotes = upvotes - 1 WHERE id = ?", (review_id,))
            cur.execute("DELETE FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
        elif vote[0] == 'downvote':
            # The user downvoted, so undo the downvote and apply the upvote
            cur.execute("UPDATE reviews SET downvotes = downvotes - 1 WHERE id = ?", (review_id,))
            cur.execute("UPDATE reviews SET upvotes = upvotes + 1 WHERE id = ?", (review_id,))
            cur.execute("UPDATE review_votes SET vote_type = 'upvote' WHERE user_id = ? AND review_id = ?", (user_id, review_id))
    else:
        # The user hasn't voted yet, so apply the upvote
        cur.execute("UPDATE reviews SET upvotes = upvotes + 1 WHERE id = ?", (review_id,))
        cur.execute("INSERT INTO review_votes (user_id, review_id, vote_type) VALUES (?, ?, 'upvote')", (user_id, review_id))

    conn.commit()
    conn.close()
    return redirect(url_for('movie_details', movie_id=movie_id))

@app.route('/movie/<int:movie_id>/downvote/<int:review_id>', methods=['POST'])
def downvote_review(movie_id, review_id):
    if 'username' not in session:
        flash('You need to be logged in to downvote.', 'error')
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Get the user's ID
    cur.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    # Check if the user has already voted on this review
    cur.execute("SELECT vote_type FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
    vote = cur.fetchone()

    if vote:
        if vote[0] == 'downvote':
            # The user already downvoted, so undo the downvote
            cur.execute("UPDATE reviews SET downvotes = downvotes - 1 WHERE id = ?", (review_id,))
            cur.execute("DELETE FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
        elif vote[0] == 'upvote':
            # The user upvoted, so undo the upvote and apply the downvote
            cur.execute("UPDATE reviews SET upvotes = upvotes - 1 WHERE id = ?", (review_id,))
            cur.execute("UPDATE reviews SET downvotes = downvotes + 1 WHERE id = ?", (review_id,))
            cur.execute("UPDATE review_votes SET vote_type = 'downvote' WHERE user_id = ? AND review_id = ?", (user_id, review_id))
    else:
        # The user hasn't voted yet, so apply the downvote
        cur.execute("UPDATE reviews SET downvotes = downvotes + 1 WHERE id = ?", (review_id,))
        cur.execute("INSERT INTO review_votes (user_id, review_id, vote_type) VALUES (?, ?, 'downvote')", (user_id, review_id))

    conn.commit()
    conn.close()
    return redirect(url_for('movie_details', movie_id=movie_id))

@app.route('/movie/<int:movie_id>/undo_upvote/<int:review_id>', methods=['GET'])
def undo_upvote_review(movie_id, review_id):
    if 'username' not in session:
        flash('You need to be logged in to undo an upvote.', 'error')
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Get the user's ID
    cur.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    # Check if the user has already upvoted this review
    cur.execute("SELECT vote_type FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
    vote = cur.fetchone()

    if vote and vote[0] == 'upvote':
        # Remove the upvote
        cur.execute("UPDATE reviews SET upvotes = upvotes - 1 WHERE id = ?", (review_id,))
        cur.execute("DELETE FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
        conn.commit()

    conn.close()
    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/movie/<int:movie_id>/undo_downvote/<int:review_id>', methods=['GET'])
def undo_downvote_review(movie_id, review_id):
    if 'username' not in session:
        flash('You need to be logged in to undo a downvote.', 'error')
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Get the user's ID
    cur.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    # Check if the user has already downvoted this review
    cur.execute("SELECT vote_type FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
    vote = cur.fetchone()

    if vote and vote[0] == 'downvote':
        # Remove the downvote
        cur.execute("UPDATE reviews SET downvotes = downvotes - 1 WHERE id = ?", (review_id,))
        cur.execute("DELETE FROM review_votes WHERE user_id = ? AND review_id = ?", (user_id, review_id))
        conn.commit()

    conn.close()
    return redirect(url_for('movie_details', movie_id=movie_id))

@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('query', '')
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM movies WHERE title LIKE ?", ('%' + query + '%',))
    movies = cur.fetchall()
    conn.close()

    return jsonify([{'id': movie[0], 'title': movie[1]} for movie in movies])

@app.route('/searched_movies/')
def searched_movies():
    query = request.args.get('query', '')
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Fetch the searched movie
    cur.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + query + '%',))
    searched_movies = cur.fetchall()

    recommended_movies = []
    if searched_movies:
        movie_id = searched_movies[0][0]  # Assuming id is the first column
        recommended_movies = get_recommendations(movie_id)

    conn.close()

    # Convert the searched movie data to dictionary format
    searched_movies = [
        {
            'id': movie[0],
            'title': movie[1],
            'backdrop_path': movie[16],  # Adjust based on your column order
            'release_date': movie[6],
            'genres': movie[3],
            'vote_average': movie[11],
            'overview': movie[6]  # Assuming overview is the 7th column
        } for movie in searched_movies
    ]

    return render_template('searched_movies.html', query=query, searched_movies=searched_movies, recommended_movies=recommended_movies)

@app.route('/admin/logs')
def admin_logs():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT logs.id, logs.event_type, logs.details, logs.timestamp, users.username FROM logs LEFT JOIN users ON logs.user_id = users.id ORDER BY logs.timestamp DESC")
    logs = cur.fetchall()
    conn.close()
    return render_template('admins/admin_logs.html', logs=logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
