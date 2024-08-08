from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from database import get_db_connection
from datetime import *

studio_bp = Blueprint('studio', __name__, url_prefix='/studio')

@studio_bp.route('/')
def studio_home():
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM studios WHERE user_id = ?", (user_id,))
    studio = cur.fetchone()
    conn.close()

    if studio:
        return render_template('studios/studio_dashboard.html', studio=studio)
    else:
        return redirect(url_for('studio.create_studio'))

@studio_bp.route('/create', methods=['GET', 'POST'])
def create_studio():
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        studio_name = request.form['studio_name']
        studio_country = request.form['studio_country']
        business_email = request.form['business_email']
        user_id = session['user_id']
        created_at = datetime.now().strftime('%Y-%m-%d')
        verified = 0

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO studios (studio_name, studio_country, business_email, user_id, created_at, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (studio_name, studio_country, business_email, user_id, created_at, verified))
        conn.commit()
        conn.close()

        flash('Studio created successfully!', 'success')
        return redirect(url_for('studio.studio_home'))

    return render_template('studios/create_studio.html')

@studio_bp.route('/studio/edit', methods=['GET', 'POST'])
def edit_studio():
    """
    Route to edit an existing studio.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM studios WHERE user_id = ?", (user_id,))
    studio = cur.fetchone()
    
    if request.method == 'POST':
        studio_name = request.form['studio_name']
        studio_country = request.form['studio_country']
        business_email = request.form['business_email']
        
        cur.execute("UPDATE studios SET studio_name = ?, studio_country = ?, business_email = ? WHERE user_id = ?",
                    (studio_name, studio_country, business_email, user_id))
        conn.commit()
        conn.close()
        
        flash('Studio updated successfully!', 'success')
        return redirect(url_for('studio.studio_home'))
    
    conn.close()
    return render_template('studios/edit_studio.html', studio=studio)

@studio_bp.route('/my_movies')
def my_movies():
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM studios WHERE user_id = ?", (user_id,))
    studio = cur.fetchone()
    
    if studio:
        studio_id = studio['id']
        cur.execute("SELECT id, title, budget, genres, homepage, overview, release_date, revenue, runtime, spoken_languages, tagline, poster_path, backdrop_path, status FROM movies WHERE studio_id = ?", (studio_id,))
        movies = cur.fetchall()
    else:
        movies = []
    
    conn.close()

    return render_template('studios/my_movies.html', studio=studio, movies=movies)

@studio_bp.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form['title']
        budget = request.form['budget']
        genres = request.form['genres'].split(',')
        homepage = request.form['homepage']
        overview = request.form['overview']
        release_date = request.form['release_date']
        revenue = request.form['revenue']
        runtime = request.form['runtime']
        spoken_languages = request.form['spoken_languages'].split(',')
        tagline = request.form['tagline']
        poster_path = request.form['poster_path']
        backdrop_path = request.form['backdrop_path']
        status = request.form['status']
        user_id = session['user_id']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO movies (title, budget, genres, homepage, overview, release_date, revenue, runtime, 
                                spoken_languages, tagline, poster_path, backdrop_path, status, studio_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    (SELECT id FROM studios WHERE user_id = ?))
        ''', (title, budget, str(genres), homepage, overview, release_date, revenue, runtime, 
              str(spoken_languages), tagline, poster_path, backdrop_path, status, user_id))
        conn.commit()
        conn.close()

        flash('Movie added successfully!', 'success')
        return redirect(url_for('studio.my_movies'))

    return render_template('studios/add_movie.html')


@studio_bp.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cur.fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        budget = request.form['budget']
        genres = request.form['genres'].split(',')
        homepage = request.form['homepage']
        overview = request.form['overview']
        release_date = request.form['release_date']
        revenue = request.form['revenue']
        runtime = request.form['runtime']
        spoken_languages = request.form['spoken_languages'].split(',')
        tagline = request.form['tagline']
        poster_path = request.form['poster_path']
        backdrop_path = request.form['backdrop_path']
        status = request.form['status']

        cur.execute('''
            UPDATE movies 
            SET title = ?, budget = ?, genres = ?, homepage = ?, overview = ?, release_date = ?, 
                revenue = ?, runtime = ?, spoken_languages = ?, tagline = ?, poster_path = ?, 
                backdrop_path = ?, status = ?
            WHERE id = ?
        ''', (title, budget, str(genres), homepage, overview, release_date, revenue, runtime, str(spoken_languages), tagline, poster_path, backdrop_path, status, movie_id))
        conn.commit()
        conn.close()

        flash('Movie updated successfully!', 'success')
        return redirect(url_for('studio.my_movies'))

    conn.close()
    return render_template('studios/edit_movie.html', movie=movie)


@studio_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('studio.my_movies'))

