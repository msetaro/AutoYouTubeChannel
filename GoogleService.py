import datetime
import pickle
import os

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def upload_video(title='', description='', tags=[], outputFile='', googleAPI=None):
    now = datetime.datetime.now()
    upload_date_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute,
                                         int(now.second)).isoformat() + '.000Z'
    print('Uploading video...')
    request_body = {
        'snippet': {
            'categoryId': 23,
            'title': title,
            'description': description,
            'tags': tags
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        },
        'notifySubscribers': False
    }

    mediaFile = MediaFileUpload(outputFile, chunksize=-1, resumable=True)

    response_upload = googleAPI.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    ).execute()

    print("Upload Successful!")


def create_service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt


def init_credentials():
    # Handle GoogleAPI oauthStuff
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    client_secrets_file = "secret.json"
    TOKEN_NAME = 'token.json'

    print("Handling GoogleAPI")

    creds = None
    # The file token1.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_NAME):
        creds = Credentials.from_authorized_user_file(TOKEN_NAME, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(TOKEN_NAME, 'w') as token:
            token.write(creds.to_json())

    googleAPI = build('youtube', 'v3', credentials=creds)
    return googleAPI
