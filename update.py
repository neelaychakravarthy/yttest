from yt import auth, db, models, routes
import flask

credentials = models.Credentials.query.get(1)

#update reporting jobs and their reports
youtube_reporting = auth.get_google_api('youtubereporting', 'v1', credentials={
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id" : credentials.client_id,
        "client_secret" : credentials.client_secret,
        "scopes" : routes.split_scopes(credentials)
})
jobs = youtube_reporting.jobs().list().execute()
for job in jobs['jobs']:
    exists = models.Jobs.query.filter_by(id=job['id']).first()
    if exists is None:
        db_job = models.Jobs(id=job['id'], report_type_id=job['reportTypeId'], name=job['name'], create_time=job['createTime'])
        db.session.add(db_job)
        db.session.commit()
    job_id = job['id']
    reports=youtube_reporting.jobs().reports().list(jobId=job_id).execute()
    if reports:
        for report in reports['reports']:
            exists = models.Reports.query.filter_by(id=report['id']).first()
            if exists is None:
                db_report = models.Reports(id=report['id'], job_id=report['jobId'], start_time=report['startTime'], end_time=report['endTime'], create_time=report['createTime'], download_url=report['downloadUrl'])
                db.session.add(db_report)
                db.session.commit()

#update videos and their data
youtube_data = auth.get_google_api('youtube', 'v3', credentials={
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id" : credentials.client_id,
        "client_secret" : credentials.client_secret,
        "scopes" : routes.split_scopes(credentials)
})
response = youtube_data.search().list(part="snippet", type="video", forMine="true").execute()
total=response["pageInfo"]["totalResults"]
count = 0
if response:
    while(count < total):
        for video in response["items"]:
            count+=1
            exists = models.Videos.query.filter_by(id=video['id']["videoId"]).first()
            video_id = video['id']['videoId']
            video_data = youtube_data.videos().list(id=video_id,part="snippet,statistics,status,suggestions").execute()
            if exists is None:
                db_Video = models.Videos(id=video['id']["videoId"], name=video["snippet"]["title"])
                db.session.add(db_Video)
                db.session.commit()
                db_data = models.VideoStats(id=video_id, views=video_data['items'][0]['statistics']['viewCount'], likes=video_data['items'][0]['statistics']['likeCount'], dislikes=video_data['items'][0]['statistics']['viewCount'], comments=video_data['items'][0]['statistics']['commentCount'])
                db.session.add(db_data)
                db.session.commit()
            else:
                exists = models.VideoStats.query.filter_by(id=video_id).first()
                if exists:
                    if(exists.views != video_data['items'][0]['statistics']['viewCount']):
                        exists.views = video_data['items'][0]['statistics']['viewCount']
                    if(exists.likes != video_data['items'][0]['statistics']['likeCount']):
                        exists.likes = video_data['items'][0]['statistics']['likeCount']
                    if(exists.dislikes != video_data['items'][0]['statistics']['viewCount']):
                        exists.dislikes = video_data['items'][0]['statistics']['viewCount']
                    if(exists.comments != video_data['items'][0]['statistics']['commentCount']):
                        exists.comments = video_data['items'][0]['statistics']['commentCount']
                    db.session.commit()
                else:
                    db_data = models.VideoStats(id=video_id, views=video_data['items'][0]['statistics']['viewCount'], likes=video_data['items'][0]['statistics']['likeCount'], dislikes=video_data['items'][0]['statistics']['viewCount'], comments=video_data['items'][0]['statistics']['commentCount'])
                    db.session.add(db_data)
                    db.session.commit()
        if("nextPageToken" in response):
            response = youtube_data.search().list(part="snippet", type="video", forMine="true", pageToken=response["nextPageToken"]).execute()