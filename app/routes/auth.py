from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import config

bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('authenticated'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == config.SITE_PASSWORD:
            session['authenticated'] = True
            session.permanent = True
            flash('התחברת בהצלחה!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('סיסמה שגויה', 'error')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('התנתקת בהצלחה', 'success')
    return redirect(url_for('auth.login'))
