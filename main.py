from flask import Flask, redirect, url_for, session, flash, render_template
import os
import sqlite3

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
    Home route for users. Displays user details if logged in.
    """
    if 'username' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT username, first_name, last_name FROM users WHERE username = ?", (session['username'],))
    user = cur.fetchone()
    conn.close()

    return render_template('home.html', user={'username': user[0], 'first_name': user[1], 'last_name': user[2]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
