from functools import wraps
from flask import session, redirect,url_for

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect('/admin-login')
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin is logged in
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))

        return f(*args, **kwargs)

    return decorated_function