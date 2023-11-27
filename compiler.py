import os
import random
from collections import defaultdict
from os.path import isfile, join
from shlex import join

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip


def extract_acc(filepath):
    try:
        s = filepath.split("/")[-1].split("-")
        acc = "-".join(s[1:(2 + (len(s) - 4))])
        return acc
    except:
        return ""


# generateTimeRange converts float seconds to a range of form @MM:SS
def generate_time_range(duration, clipDuration):
    preHour = int(duration / 60)
    preMin = int(duration % 60)
    preTime = str(preHour // 10) + str(preHour % 10) + ":" + str(preMin // 10) + str(preMin % 10)

    duration += clipDuration
    postHour = int(duration / 60)
    postMin = int(duration % 60)
    postTime = str(postHour // 10) + str(postHour % 10) + ":" + str(postMin // 10) + str(postMin % 10)

    # return "@" + preTime + " - " + "@" + postTime
    return "@" + preTime


# makeCompilation takes videos in a folder and creates a compilation with max length totalVidLength
def make_compilation(path="./",
                     introName='',
                     outroName='',
                     totalVidLength=10 * 60,
                     maxClipLength=20,
                     minClipLength=5,
                     outputFile="output.mp4",
                     customAudio=False):
    allVideos = []
    seenLengths = defaultdict(list)
    totalLength = 0
    for fileName in os.listdir(path):

        filePath = join(path, fileName);
        if isfile(filePath) and fileName.endswith(".mp4"):
            if os.stat(filePath).st_size < 5000:
                continue

            # Destination path
            clip = VideoFileClip(filePath)
            # clip = clip.resize((1920, 1080), PIL.Image.LANCZOS)
            duration = clip.duration
            if duration <= maxClipLength and duration >= minClipLength:
                allVideos.append(clip)
                seenLengths[duration].append(fileName)
                totalLength += duration

    print("Total Length: " + str(totalLength))

    random.shuffle(allVideos)

    duration = 0
    # Add intro vid
    videos = []
    if introName != '':
        introVid = VideoFileClip("./" + introName)
        videos.append(introVid)
        duration += introVid.duration

    description = ""
    # Create videos
    for clip in allVideos:
        timeRange = generate_time_range(duration, clip.duration)
        acc = extract_acc(clip.filename)
        description += timeRange + " : @" + acc + "\n"
        duration += clip.duration
        videos.append(clip)
        if duration >= totalVidLength:
            # Just make one video
            break

    # Add outro vid
    if outroName != '':
        outroVid = VideoFileClip("./" + outroName)
        videos.append(outroVid)

    finalClip = concatenate_videoclips(videos, method="compose")

    audio_path = "/tmp/temoaudiofile.m4a"

    # take a random section of the lofi that's as long as the video

    if customAudio:
        print('Using custom music instead of the audio from each reel')
        lofi_audio = AudioFileClip('./custom_music.mp3')
        lofi_start = random.randrange(0, (round(lofi_audio.duration) - round(totalLength)))

        finalClip.audio = lofi_audio.subclip(lofi_start, (lofi_start + round(totalLength)))

    # Create compilation
    finalClip.write_videofile(outputFile, threads=8, temp_audiofile=audio_path, remove_temp=True, codec="libx264",
                              audio_codec="aac")

    return description