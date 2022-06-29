
import os
from yt import app

if __name__ == "__main__":
     
     #for testing purposes
     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

     app.run('localhost', 8080, debug=True)