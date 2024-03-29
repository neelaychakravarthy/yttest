import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import flask

CLIENT_SECRETS_FILE = "yt/json/client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/yt-analytics-monetary.readonly', 'https://www.googleapis.com/auth/yt-analytics.readonly', 'https://www.googleapis.com/auth/youtube.force-ssl']
#SCOPES = 'https://www.googleapis.com/auth/yt-analytics-monetary.readonly, https://www.googleapis.com/auth/yt-analytics.readonly, https://www.googleapis.com/auth/youtube.force-ssl'

def get_auth_url():

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_url  = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    return authorization_url

def get_credentials(state):

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials

def get_google_api(API_SERVICE_NAME, API_VERSION, credentials):
    google_credentials = google.oauth2.credentials.Credentials(credentials["token"], refresh_token=credentials["refresh_token"],
    token_uri=credentials["token_uri"], client_id=credentials["client_id"], client_secret=credentials["client_secret"], scopes=credentials["scopes"])
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=google_credentials)