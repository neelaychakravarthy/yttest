import flask
import requests

from yt import app, auth, db, models
import json

#TODO: Job creation page, for if there are no jobs

#TODO: Database migration

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
    token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret, scopes=credentials.scopes)
    db.session.add(db_creds)
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

    for job in jobs['jobs']:

        exists = models.Jobs.query.filter_by(id=job['id']).first()
        if exists is None:
            db_job = models.Jobs(id=job['id'], report_type_id=job['reportTypeId'], name=job['name'], create_time=job['createTime'])
            db.session.add(db_job)
            db.session.commit()
    
    jobs = models.Jobs.query.all()
    return flask.render_template('reporting_jobs.html', jobs=jobs)

@app.route('/delete_job', defaults={'job_id' : 'NONE'})
@app.route('/delete_job/<string:job_id>')
def delete_job(job_id):
    credentials = models.Credentials.query.get(1)
    if credentials is None:
        return flask.redirect(flask.url_for('authorize'))
    youtube_reporting = auth.get_google_api('youtubereporting', 'v1', credentials=credentials)
    youtube_reporting.jobs().delete(jobId=job_id).execute()
    models.Jobs.query.filter_by(id=job_id).delete()
    db.session.commit()
    return flask.redirect(flask.url_for('ytreports'))

@app.route('/reports', defaults={'job_id' : 'NONE'})
@app.route('/reports/<string:job_id>')
def reports(job_id):
    if job_id == 'NONE':
        return 'No Job ID provided. Please try again'
    else:
        print(job_id)
        credentials = models.Credentials.query.get(1)
        if credentials is None:
            return flask.redirect(flask.url_for('authorize'))

        youtube_reporting = auth.get_google_api('youtubereporting', 'v1', credentials=credentials)
        reports=youtube_reporting.jobs().reports().list(jobId=job_id).execute()
        if reports:
            for report in reports['reports']:
                exists = models.Reports.query.filter_by(id=report['id']).first()
                if exists is None:
                    db_report = models.Reports(id=report['id'], job_id=report['jobId'], start_time=report['startTime'], end_time=report['endTime'], create_time=report['createTime'], download_url=report['downloadUrl'])
                    db.session.add(db_report)
                    db.session.commit()
        
        reports = models.Reports.query.filter_by(job_id=job_id)
        return flask.render_template('reports.html', reports=reports)

@app.route('/download', defaults={'url' : 'NONE'})
@app.route('/download/<path:url>')
def download(url):
    if url == None:
        return 'Something went wrong. Please try again.'
    else:
        token = 'Bearer ' + models.Credentials.query.get(1).token
        headers = {'Authorization' : token, 'Accept-Encoding' : 'gzip'}
        response = requests.get(url, headers=headers)
        return 'Content of Report: \n' + str(response.content)

@app.route('/create_job', methods=['GET', 'POST'])
def create_job():
    if flask.request.method == 'GET':
        return flask.render_template('create_job.html')
    if flask.request.method == 'POST':
        report_type=flask.request.form.get('report_type')
        name=flask.request.form.get('name')

        if report_type is None or name is None:
            return 'Please input a valid name or report type.'
        credentials = models.Credentials.query.get(1)
        if credentials is None:
            return flask.redirect(flask.url_for('authorize'))
        youtube_reporting = auth.get_google_api('youtubereporting', 'v1', credentials=credentials)
        youtube_reporting.jobs().create(body=dict(reportTypeId=report_type, name=name)).execute()
        return flask.redirect(flask.url_for('ytreports'))
            

@app.route('/ytanalytics')
def ytanalytics():
    pass