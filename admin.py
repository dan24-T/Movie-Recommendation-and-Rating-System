from flask import Blueprint, render_template, url_for, request, flash, redirect, session
from database import get_db_connection
import math

# Create a Blueprint for admin-related routes
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
    Admin users management route. Display all users for admin.
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
    Admin movies management route.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
    
    # Add logic to fetch movies from the database if needed
    return render_template('admins/movies.html')

@admin.route('/admin/studios/', methods=['GET'])
def admin_studios():
    """
    Admin studios management route. Display all studios for admin.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT s.id, s.name, s.country, s.business_email, s.created_at, s.is_verified, u.username 
        FROM studios s 
        JOIN users u ON s.user_id = u.id
    ''')
    studios = cur.fetchall()
    conn.close()

    return render_template('admins/studios.html', studios=studios)

@admin.route('/admin/verify_studio/<int:studio_id>/', methods=['POST'])
def verify_studio(studio_id):
    """
    Route to verify a studio.
    """
    if 'username' not in session or not session.get('is_admin'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE studios SET verified = 1 WHERE id = ?", (studio_id,))
    conn.commit()
    conn.close()

    flash('Studio verified successfully.', 'success')
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
