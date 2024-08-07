from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import sqlite3
from database import get_db_connection

# Create a Blueprint for studio-related routes
studio = Blueprint('studio', __name__)

@studio.route('/studio/')
def studio_home():
    """
    Studio home route. Show studio details if exists, else show a link to create studio.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM studios WHERE user_id = ?", (user_id,))
    studio = cur.fetchone()
    conn.close()
    
    return render_template('studios/studio_home.html', studio=studio)

@studio.route('/studio/create', methods=['GET', 'POST'])
def create_studio():
    """
    Route to create a new studio.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        studio_name = request.form['studio_name']
        studio_country = request.form['studio_country']
        business_email = request.form['business_email']
        additional_info = request.form['additional_info']
        created_date = datetime.now().strftime("%Y-%m-%d")
        verified = 0  # Studio is not verified initially
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO studios (name, country, business_email, additional_info, user_id, created_date, verified) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (studio_name, studio_country, business_email, additional_info, user_id, created_date, verified))
        conn.commit()
        conn.close()
        
        flash('Studio created successfully!', 'success')
        return redirect(url_for('studio.studio_home'))
    
    return render_template('studios/create_studio.html')

@studio.route('/studio/edit', methods=['GET', 'POST'])
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
        additional_info = request.form['additional_info']
        
        cur.execute("UPDATE studios SET name = ?, country = ?, business_email = ?, additional_info = ? WHERE user_id = ?",
                    (studio_name, studio_country, business_email, additional_info, user_id))
        conn.commit()
        conn.close()
        
        flash('Studio updated successfully!', 'success')
        return redirect(url_for('studio.studio_home'))
    
    conn.close()
    return render_template('studios/edit_studio.html', studio=studio)

@studio.route('/studio/movies/')
def my_movies():
    """
    My Movies route. Display welcome message and prompt to create studio if not exists.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM studios WHERE user_id = ?", (user_id,))
    studio = cur.fetchone()
    conn.close()

    return render_template('studios/my_movies.html', studio=studio)

@studio.route('/studio/add_movie', methods=['GET', 'POST'])
def add_movie():
    """
    Route to add a new movie.
    """
    if 'user_id' not in session:
        flash('User ID is missing in session.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        budget = request.form['budget']
        genres = request.form['genres']
        homepage = request.form['homepage']
        keywords = request.form['keywords']
        overview = request.form['overview']
        production_companies = request.form['production_companies']
        production_countries = request.form['production_countries']
        release_date = request.form['release_date']
        revenue = request.form['revenue']
        runtime = request.form['runtime']
        spoken_languages = request.form['spoken_languages']
        tagline = request.form['tagline']

        # Set default values for fields that are no longer part of the form
        original_language = spoken_languages
        original_title = title
        status = 'New'
        popularity = 0
        vote_average = 0
        vote_count = 0

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO movies (title, budget, genres, homepage, keywords, original_language, original_title, overview, popularity, 
                                production_companies, production_countries, release_date, revenue, runtime, spoken_languages, status, 
                                tagline, vote_average, vote_count) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, budget, genres, homepage, keywords, original_language, original_title, overview, popularity, production_companies,
              production_countries, release_date, revenue, runtime, spoken_languages, status, tagline, vote_average, vote_count))
        conn.commit()
        conn.close()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('studio.my_movies'))

    return render_template('studios/add_movie.html')
