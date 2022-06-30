import flask

from yt import app, auth, db, models
import json


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

    models.Credentials.query.delete()
    db.session.commit()

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
    return flask.render_template('api_select.html')

@app.route('/ytreports')
def ytreports():
    credentials = models.Credentials.query.get(1)
    if credentials is None:
        return flask.redirect(flask.url_for('authorize'))
    
    youtube_reporting = auth.get_google_api('youtubereporting', 'v1', credentials=credentials)
    jobs = youtube_reporting.jobs().list().execute()

    #TODO: Change the way we store SCOPES. When refreshing credentials, google auth does not recognize the scope object we use. We can do it one at
    # a time, as recomended, or we can store it in the credentials model itself with PickleType. Either way, we must remove the Scopes model.

  #  for job in jobs:
        # print(job)
        # exists = db.session.query(models.Jobs.id).filter_by(json.loads(job).id).first()
        # if exists is None:
        #     db.session.add(job)
        #     db.commit()

@app.route('/ytanalytics')
def ytanalytics():
    pass