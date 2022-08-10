from yt import db

class Credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    refresh_token = db.Column(db.String(500), unique=True)
    token_uri = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.String(100), unique=True, nullable=False)
    client_secret = db.Column(db.String(100), unique=True, nullable=False)
    scopes = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Credentials[ID: '{self.id}', URI: '{self.token_uri}', SCOPES: '{self.scopes}', CLIENT_ID: '{self.client_id}', TOKEN: '{self.token}']"

class Jobs(db.Model):
    id = db.Column(db.String(40), primary_key=True, autoincrement=False)
    report_type_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.String(40), nullable=False, unique=True)

    def __repr__(self):
        return f"Job[ID: '{self.id}', TYPE_ID: '{self.report_type_id}', NAME: '{self.name}', CREATED: '{self.create_time}']"

class Reports(db.Model):
    id = db.Column(db.String(40), primary_key=True, autoincrement=False)
    job_id = db.Column(db.String(40), nullable=False)
    start_time = db.Column(db.String(40), nullable=False)
    end_time = db.Column(db.String(40), nullable=False)
    create_time = db.Column(db.String(40), unique=True, nullable=False)
    download_url = db.Column(db.String(1000), nullable=False, unique=True)

class Videos(db.Model):
    id = db.Column(db.String(12), primary_key=True, autoincrement=False)
    name = db.Column(db.String(100), nullable=False)

class VideoStats(db.Model):
    id = db.Column(db.String(12), primary_key=True, autoincrement=False)
    views = db.Column(db.String(10), nullable=False)
    likes = db.Column(db.String(10), nullable=False)
    dislikes = db.Column(db.String(10), nullable=False)
    comments = db.Column(db.String(10), nullable=False)