from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from authlib.integrations.flask_client import OAuth
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
import logging
import os
import requests
from . import db
from .models import User

load_dotenv()

bp = Blueprint('auth', __name__)

oauth = OAuth(current_app).register(
    'MCGJ',
    server_metadata_url=os.getenv("SERVER_URL"),
    client_kwargs={
        "scope": os.getenv("CLIENT_SCOPE"),
    },
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)

@bp.route('/login_test')
def login():
    if current_user.is_authenticated:
        return current_user.name
    else:
        return 'Not logged in'

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('mcgj.index'))

@bp.route('/auth/oauth')
def auth_oauth_redirect():
    callback = os.getenv('CLIENT_CALLBACK')
    return oauth.authorize_redirect(callback)

@bp.route('/sessions/<session_id>/auth/oauth')
def session_auth_oauth_redirect(session_id):
    session['auth_session'] = session_id
    callback = os.getenv('CLIENT_CALLBACK')
    return oauth.authorize_redirect(callback)

@bp.route('/auth/callback', methods=['GET', 'POST'])
def auth_oauth_callback():
    # Process the results of a successful OAuth2 authentication"
    try:
        token = oauth.authorize_access_token()
    except HTTPException:
        logging.error(
            'Error %s parsing OAuth2 response: %s',
            request.args.get('error', '(no error code)'),
            request.args.get('error_description', '(no error description'),
        )
        return (jsonify({
            'message': 'Access Denied',
            'error': request.args.get('error', '(no error code)'),
            'error_description': request.args.get('error_description', '(no error description'),
        }), 403)
  
    user = User(with_id=oauth.userinfo()["sub"])
    user.name = oauth.userinfo()["name"]

    # yeah maybe this shouldn't be a one-off query
    user_query = "SELECT * FROM users WHERE id = ?"
    user_row = db.query(sql=user_query, args=[user.id])
    if not user_row:
        user.insert()
    else:
        # in case the name has updated on the RC side
        user.update()
    login_user(user)
    if 'auth_session' in session:
        return redirect(url_for('mcgj.render_session', session_id=session['auth_session']))
    else:
        return redirect(url_for('mcgj.index'))
