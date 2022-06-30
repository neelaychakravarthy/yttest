import flask

from yt import app, auth, db, models


@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/authorize')
def authorize():
    authorization_url, state= auth.get_auth_url()
    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/callback')
def callback():
    
    state = flask.session['state']
    credentials = auth.get_credentials(state)
    db_creds = models.Credentials(token=credentials.token, refresh_token=credentials.refresh_token, 
    token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret)
    db.session.add(db_creds)
    db.session.commit()
    for scopes in credentials.scopes:
        db_scope = models.Scopes(credential_id=db_creds.id, scope=scopes)
        db.session.add(db_scope)
    db.session.commit()

    return flask.render_template('callback.html')

@app.route('/api_select')
def api_select():
    pass

@app.route('/ytanalytics')
def ytanalytics():
    pass

@app.route('/ytreports')
def ytreports():
    pass