import datetime
import os
import random
import shutil
from pathlib import Path
from dotenv import load_dotenv

from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from moviepy.editor import VideoFileClip
from moviepy.video.fx.resize import resize

from compiler import make_compilation
from GoogleService import upload_video, init_credentials

VideoFileClip.resize = resize
load_dotenv()

# Instagram
ACCOUNT_USERNAME = os.getenv("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


# default is lofi music, if you want to use something else,
# make sure its long (> 1hr) and name the file custom_music.mp3
USE_CUSTOM_AUDIO = True

INTRO_VID = '' # SET AS '' IF YOU DONT HAVE ONE
OUTRO_VID = ''

# how many reels to scrape per follower
REELS_PER_FOLLOWER = 5

# Youtube video details
title = ''
description = ''
tags = []






# init
num_to_month = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "June",
    7: "July",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}
now = datetime.datetime.now()

videoDirectory = "./AutoScraper" + num_to_month[now.month].upper() + "_" + str(now.year) + "_V" + str(now.day) + "/"
outputFile = "./" + num_to_month[now.month].upper() + str(now.day) + "_" + str(now.year) + "_" + str(now.hour) + str(now.minute) + ".mp4"

def scrape_reels():
    cl = Client()
    cl.delay_range = [3, 5]

    # cookie storage
    cookie_path = './instagram_cookie.json'
    if not os.path.isfile(cookie_path):
        os.open(cookie_path, os.O_CREAT)

    session = None
    try:
        session = cl.load_settings(Path(cookie_path))
    except Exception:
        session = None

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                print("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
            login_via_session = True
        except Exception as e:
            print("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            print("Attempting to login via username and password. username: %s" % ACCOUNT_USERNAME)
            if cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD):
                login_via_pw = True
        except Exception as e:
            print("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")

    user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
    print(f'Successfully logged in as {ACCOUNT_USERNAME}, user ID: {user_id}')

    # get all following
    following = cl.user_following(user_id)

    if len(following) < 10:
        raise Exception('Error, not following more than 10 people')


    print(
        f'User {ACCOUNT_USERNAME} is following {len(following)} accounts, beginning reel scrape at {REELS_PER_FOLLOWER} reels per account...')

    # foreach person following, grab the last n number of reels posted
    all_reels = []
    total_reels_num = 0
    for user in random.sample(following, 10):
        videos = cl.user_clips(user, REELS_PER_FOLLOWER)
        all_reels.append(videos)
        total_reels_num += len(videos)
        print(f'Scraped {len(videos)} reels from {following[user].username}, total reels: {total_reels_num}')

    try:
        print('Creating video dump directory')
        os.mkdir(videoDirectory)
        print('Video dump directory created!')
    except OSError as error:
        print('Directory already created!')

    # download the reels to local storage
    print('Downloading reels to local storage...')
    for i in range(len(all_reels)):
        for j in range(REELS_PER_FOLLOWER):
            url = all_reels[i][j].video_url
            cl.clip_download_by_url(url, folder=Path(videoDirectory))
            total_reels_num -= 1
            print(f'Downloaded reel -- {total_reels_num} remaining')


    print(f'Gathered {len(all_reels) * REELS_PER_FOLLOWER} reels from {len(following)} users')


#######################################################################################################################
google = init_credentials()
scrape_reels()
# put all the reels into one big video
print("Making Compilation...")
make_compilation(path=videoDirectory,
                 introName=INTRO_VID,
                 outroName=OUTRO_VID,
                 totalVidLength=13*60,
                 maxClipLength=19,
                 minClipLength=5,
                 outputFile=outputFile,
                 customAudio=USE_CUSTOM_AUDIO)
print("Made Compilation!")
shutil.rmtree(videoDirectory)

# upload video to youtube
upload_video(title=title, description=description, tags=tags, outputFile=outputFile, googleAPI=google)