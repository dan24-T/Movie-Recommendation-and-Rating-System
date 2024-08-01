from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from database import get_db_connection

# Create a Blueprint for authentication-related routes
auth = Blueprint('auth', __name__)

@auth.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Handle user login. Clear session and authenticate user based on email/username and password.
    """
    session.pop('username', None)
    session.pop('is_admin', None)
    
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? OR email = ?", (email_or_username, email_or_username))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['user_id'] = user['id']  # Store user_id in session
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email/username or password.', 'error')
    
    return render_template('login.html')

@auth.route('/signup/', methods=['GET', 'POST'])
def signup():
    """
    Handle user signup. Validate and save new user information.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        country = request.form['country']
        dob = request.form['dob']
        gender = request.form['gender']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.signup'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password, first_name, last_name, email, country, dob, gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (username, hashed_password, first_name, last_name, email, country, dob, gender))
            conn.commit()
            conn.close()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists.', 'error')
    
    return render_template('signup.html')

@auth.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    """
    Handle forgotten password. Send a reset link to the user's email if it exists.
    """
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        
        if user:
            session['reset_email'] = email
            flash('Password reset link has been sent to your email.', 'success')
            # Send email logic goes here
            return redirect(url_for('auth.reset_password'))
        else:
            flash('No account found with that email.', 'error')
    return render_template('forgot_password.html')

@auth.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    """
    Handle password reset. Validate and update the user's password.
    """
    if 'reset_email' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.reset_password'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, session['reset_email']))
        conn.commit()
        conn.close()
        
        session.pop('reset_email', None)
        flash('Password has been reset. Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')

@auth.route('/logout/', methods=['POST'])
def logout():
    """
    Handle user logout. Clear session and redirect to login page.
    """
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
