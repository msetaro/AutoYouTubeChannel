# Automated YouTube Channel

This script will log you into an Instagram account, download 5 feels from 10 random followers, and merge all the reels into one big video. Then, the script can also upload the video to YouTube, if set up properly.


# Set up
1. Set your Instagram account's username and password to the respective variables in `.env`
   2. You need to be following more than 10 people on this account for the script to work
3. Find background music you want to use online. It should be ideally over an hour long. Place the file in the same directory as `main.py` and name it `custom_music.mp3`
   4. This is required so your video does not get copyright striked
5. Set up YouTube integration, watch this video here: https://youtu.be/aFwZgth790Q?si=_PYJwSzNcg9gY3C5&t=250
   6. If you don't want to upload the video to YouTube, comment out the lines in `main.py` that call `init_credentials()` and `upload_video()`


# Notes
This can very easily get you hardware banned from Instagram, preventing you from creating any new accounts (I learned the hard way).
Use with caution if you don't want your account banned. Also, consider using this infrequently and on a VPN as to not flag your account for suspicious activity. You'll know if you're banned if the script outputs something like this: `Couldn't login user using username and password: The password you entered is incorrect. Please try again. If you are sure that the password is correct, then change your IP address, because it is added to the blacklist of the Instagram Server`