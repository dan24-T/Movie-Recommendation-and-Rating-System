from flask import Blueprint, render_template, url_for, request, flash, redirect, session
from database import get_db_connection
import math

# Create a Blueprint for admin-related
admin = Blueprint('admin', __name__)

@admin.route('/admin/')
def admin_home():
    """
    Admin home route. Redirect to admin users page if the user is an admin.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('admin.admin_users'))

@admin.route('/admin/users/')
def admin_users():
    """
    Admin users management route. Display all users.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    search_query = request.args.get('search', '')
    per_page = int(request.args.get('per_page', 5))
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    if search_query:
        cur.execute("SELECT COUNT(*) FROM users WHERE username LIKE ? OR email LIKE ?", (f"%{search_query}%", f"%{search_query}%"))
        total_users = cur.fetchone()[0]
        cur.execute("SELECT id, username, email, is_admin FROM users WHERE username LIKE ? OR email LIKE ? LIMIT ? OFFSET ?", (f"%{search_query}%", f"%{search_query}%", per_page, offset))
    else:
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]
        cur.execute("SELECT id, username, email, is_admin FROM users LIMIT ? OFFSET ?", (per_page, offset))

    users = cur.fetchall()
    conn.close()
    
    total_pages = math.ceil(total_users / per_page)

    return render_template('admins/users.html', users=users, search_query=search_query, per_page=per_page, page=page, total_pages=total_pages)

@admin.route('/admin/toggle_admin/<int:user_id>/', methods=['POST'])
def toggle_admin(user_id):
    """
    Route to toggle the admin status of a user.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    
    if user:
        new_status = 0 if user['is_admin'] else 1
        cur.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_status, user_id))
        conn.commit()
        flash('User admin status updated.', 'success')
    else:
        flash('User not found.', 'error')
    
    conn.close()
    return redirect(url_for('admin.admin_users'))

@admin.route('/admin/delete_user/<int:user_id>/', methods=['POST'])
def delete_user(user_id):
    """
    Route to delete a user.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash('User deleted.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin.route('/admin/movies/')
def admin_movies():
    """
    Admin movies management route with sorting and pagination.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
    
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'title')  # Default sort by title
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order is ascending
    per_page = int(request.args.get('per_page', 5))
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()
    
    if search_query:
        query = f"""
        SELECT COUNT(*) FROM movies WHERE title LIKE ? OR overview LIKE ?
        """
        cur.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        total_movies = cur.fetchone()[0]

        query = f"""
        SELECT * FROM movies WHERE title LIKE ? OR overview LIKE ?
        ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?
        """
        cur.execute(query, (f"%{search_query}%", f"%{search_query}%", per_page, offset))
    else:
        query = f"SELECT COUNT(*) FROM movies"
        cur.execute(query)
        total_movies = cur.fetchone()[0]

        query = f"SELECT * FROM movies ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        cur.execute(query, (per_page, offset))

    movies = cur.fetchall()
    conn.close()

    total_pages = math.ceil(total_movies / per_page)

    return render_template('admins/movies.html', movies=movies, search_query=search_query, sort_by=sort_by, sort_order=sort_order, per_page=per_page, page=page, total_pages=total_pages)


@admin.route('/admin/delete_movie/<int:movie_id>/', methods=['POST'])
def delete_movie(movie_id):
    """
    Route to delete a movie.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()
    
    flash('Movie deleted successfully.', 'success')
    return redirect(url_for('admin.admin_movies'))


@admin.route('/admin/studios/', methods=['GET'])
def admin_studios():
    """
    Admin studios management route. Display all studios for admin.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    # Get query parameters for pagination, sorting, and search
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'studio_name')  # Default sort by studio_name
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order is ascending
    per_page = int(request.args.get('per_page', 5))
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    # Apply search filter if needed
    if search_query:
        query = f"""
        SELECT COUNT(*) FROM studios WHERE studio_name LIKE ? OR studio_country LIKE ?
        """
        cur.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        total_studios = cur.fetchone()[0]

        query = f"""
        SELECT s.id, s.studio_name, s.studio_country, s.business_email, s.created_at, s.verified, u.username 
        FROM studios s 
        JOIN users u ON s.user_id = u.id
        WHERE s.studio_name LIKE ? OR s.studio_country LIKE ?
        ORDER BY {sort_by} {sort_order} 
        LIMIT ? OFFSET ?
        """
        cur.execute(query, (f"%{search_query}%", f"%{search_query}%", per_page, offset))
    else:
        query = "SELECT COUNT(*) FROM studios"
        cur.execute(query)
        total_studios = cur.fetchone()[0]

        query = f"""
        SELECT s.id, s.studio_name, s.studio_country, s.business_email, s.created_at, s.verified, u.username 
        FROM studios s 
        JOIN users u ON s.user_id = u.id
        ORDER BY {sort_by} {sort_order} 
        LIMIT ? OFFSET ?
        """
        cur.execute(query, (per_page, offset))

    studios = cur.fetchall()
    conn.close()

    # Calculate total pages
    total_pages = math.ceil(total_studios / per_page)

    return render_template('admins/studios.html', 
                           studios=studios, 
                           search_query=search_query, 
                           sort_by=sort_by, 
                           sort_order=sort_order, 
                           per_page=per_page, 
                           page=page, 
                           total_pages=total_pages)


@admin.route('/admin/verify_studio/<int:studio_id>/', methods=['POST'])
def verify_studio(studio_id):
    """
    Route to toggle the verification status of a studio.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the current verification status
    cur.execute("SELECT verified FROM studios WHERE id = ?", (studio_id,))
    studio = cur.fetchone()

    if studio:
        # Toggle verification status
        new_status = 0 if studio['verified'] else 1
        cur.execute("UPDATE studios SET verified = ? WHERE id = ?", (new_status, studio_id))
        conn.commit()
        flash(f"Studio {'verified' if new_status else 'unverified'} successfully.", 'success')
    else:
        flash('Studio not found.', 'error')

    conn.close()
    return redirect(url_for('admin.admin_studios'))

@admin.route('/admin/delete_studio/<int:studio_id>/', methods=['POST'])
def delete_studio(studio_id):
    """
    Route to delete a studio.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM studios WHERE id = ?", (studio_id,))
    conn.commit()
    conn.close()

    flash('Studio deleted successfully.', 'success')
    return redirect(url_for('admin.admin_studios'))
