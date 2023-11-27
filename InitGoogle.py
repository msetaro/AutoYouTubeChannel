import datetime
from GoogleService import create_service
from googleapiclient.http import MediaFileUpload

CLIENT_SECRET_FILE = 'secret.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# setup_google.py allows user to log into
service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)