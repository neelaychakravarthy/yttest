from yt import db

class Credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    refresh_token = db.Column(db.String(500), unique=True)
    token_uri = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.String(100), unique=True, nullable=False)
    client_secret = db.Column(db.String(100), unique=True, nullable=False)
    scopes = db.relationship('Scopes', backref='scopes', lazy=True)

    def __repr__(self):
        return f"Credentials[ID: '{self.id}', URI: '{self.token_uri}', SCOPES: '{self.scopes}', CLIENT_ID: '{self.client_id}', TOKEN: '{self.token}']"

class Scopes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credential_id = db.Column(db.Integer, db.ForeignKey('credentials.id'), nullable=False)
    scope = db.Column(db.String(100), nullable=False)

class Jobs(db.Model):
    id = db.Column(db.String(40), primary_key=True, autoincrement=False)
    report_type_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, unique=True)
    expire_time = db.Column(db.DateTime, nullable=False, unique=True)

    def __repr__(self):
        return f"Job[ID: '{self.id}', TYPE_ID: '{self.report_type_id}', NAME: '{self.name}', CREATED: '{self.create_time}', EXPIRES: '{self.expire_time}']"

class Reports(db.Model):
    id = db.Column(db.String(40), primary_key=True, autoincrement=False)
    job_id = db.Column(db.String(40), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    create_time = db.Column(db.DateTime, unique=True, nullable=False)
    job_expire_time = db.Column(db.DateTime, nullable=False)
    download_url = db.Column(db.String(1000), nullable=False, unique=True)

