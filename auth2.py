import os
import flask
import requests
import secrets

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "src\python\client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/yt-analytics-monetary.readonly', 'https://www.googleapis.com/auth/youtube.force-ssl', 'https://www.googleapis.com/auth/yt-analytics.readonly']
API_SERVICE_NAME = 'youtubereporting'
API_VERSION = 'v1'

app = flask.Flask(__name__)

app.secret_key = secrets.token_hex()

@app.route('/')
def index():
    return print_index_table()

@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

    youtube_reporting = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    #make api calls
    jobs = youtube_reporting.jobs().list().execute()

    #here, save credentials into database instead
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**jobs)

@app.route('/authorize')
def authorize():

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='online', include_granted_scopes='true')

    flask.session['state'] = state
    
    return flask.redirect(authorization_url)

@app.route('/callback')
def callback():

    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    #storing credentials, should eventually store in database instead
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('test_api_request'))

@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to authorize <a href="/authorize"</a> before testing the code to revoke credentials.')
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

    revoke = requests.post('http://oauth2.googleapis.com/revoke', params={'token': credentials.token}, headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = revoke.status_code
    print(status_code)
    if status_code == 200:
        return ('Credentials successfully revoked.' + print_index_table())
    else:
        return ('An error occurred.' + print_index_table())

@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
        return ('Credentials have been cleared.<br><br>' + print_index_table())

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')

if __name__ == '__main__':
    #when running in production, do not leave this enabled. For local testing purposes only.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run('localhost', 8080, debug=True)