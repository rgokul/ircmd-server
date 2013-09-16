from flask import Flask, redirect, url_for, session
from flask import make_response, request
from flask import render_template, send_from_directory
from flask import jsonify
from flask_oauth import OAuth

from simplekv.memory import DictStore
from flaskext.kvsession import KVSessionExtension

from functools import wraps

import json
import random
import string
import os

APPLICATION_NAME = 'Google+ Python Quickstart'
DEBUG = True
SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.debug_log_format = '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
						 
# See the simplekv documentation for details
store = DictStore()

# This will replace the app's session handling
KVSessionExtension(store, app)
	

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
# You must set these environmental variables in heroku (also works with foreman/honcho)
# https://devcenter.heroku.com/articles/config-vars

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']



# Must be one of the Redirect URIs from Google APIs console
REDIRECT_URI = '/authorized'

AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"

USERWHITELIST = os.environ['USERWHITELIST']
USERWHITELIST = []

oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url=AUTH_URI,
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url=TOKEN_URI,
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = session.get('access_token')
        if access_token is None:
            # Url_for takes a function as 1st argument
            # next = is the next url to redirect to after login
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/getStatus')
@login_required
def get_status():
    app.logger.info('got /sendcmd')
    return jsonify({'response':'ok'})

@app.route('/home')
@login_required
def homepage():
##    app.logger.warning(session)
    access_token = session.get('access_token')
##    if access_token is None:
##        app.logger.warning('login first')
##        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
##            app.logger.warning('login again')
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()

    resp = res.read()
    # Perform USERWHITELIST check here to prevent anyone
    # with a google account from controling your home!
##    app.logger.warning(resp)
    return render_template('home.html')

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    if resp is not None:
        access_token = resp['access_token']
        session['access_token'] = access_token, ''
        return redirect(url_for('homepage'))
    else:
        return 'Access Denied: To use this app, you will have to authorize it in your google account.'
    
@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@google.tokengetter
def get_access_token():
    app.warning('token getter')
    return session.get('access_token')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

def main():
    app.run()


if __name__ == '__main__':
    main()
