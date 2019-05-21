#import packages
from PIL import Image, ImageDraw, ImageFont
import textwrap
import pyttsx3
from moviepy.editor import *
import soundfile as sf
import tts.sapi
from random import randint
import time
import os, shutil
import mmap
import praw
import gc
from pydub import AudioSegment
from multiprocessing import Process
import librosa
import os
import json

#Number of thoughts to generate
NUMBER_OF_THOTS = 10

#Begin by starting up the voice
voice = tts.sapi.Sapi()
voice.set_voice(voice.get_voices()[0])

#Clear everything that is currently in the working directory
homePath = "Path/to/directory"
folder = '{0}/clips'.format(homePath)
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)
folder = '{0}/clips/movies'.format(homePath)
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)


#method that will create the images with the text
def makeTitleClips(
        subReddit, user, question, comments, upVoteInformation
    ):

    #use the global voice variable for timing
    global voice
    slides = []
    img = Image.new("RGB", (1920, 1080), color='white')

    #Calculate the spacing required...
    charactersInQuestion = len(question)
    lines = textwrap.wrap(question, width=28)
    d = ImageDraw.Draw(img)

    #Define dimensions of images and place subimages
    basewidth = int(1920)
    redditTop = Image.open("{0}content/topRedditTitle.png".format(homePath))
    wpercent = (basewidth/float(redditTop.size[0]))
    hsize = int((float(redditTop.size[1])*float(wpercent)))
    redditTop = redditTop.resize((basewidth,hsize), Image.ANTIALIAS)

    basewidth = int(1920)
    redditBottom = Image.open("{0}content/bottomRedditTitle.png".format(homePath))
    wpercent = (basewidth/float(redditBottom.size[0]))
    hsize = int((float(redditBottom.size[1])*float(wpercent)))
    redditBottom = redditBottom.resize((basewidth,hsize), Image.ANTIALIAS)

    img.paste(redditTop,(0,0))

    #begin placing text over image in certain fonts
    userFont = ImageFont.truetype('verdana.ttf', size=55)
    askRedditFont = ImageFont.truetype('verdanab.ttf', size=55)
    d.text((300, 60), subReddit, font=askRedditFont, fill=(100, 100, 100))
    d.text((300, 130), user, font=userFont, fill=(100, 100, 100))

    questionFont = ImageFont.truetype('verdanab.ttf', 100)


    img.paste(redditBottom, (0, 650))

    #place text for upvote/comments labels
    d.text((920, 920), comments, font=askRedditFont, fill=(150, 150, 150))
    d.text((200, 920), upVoteInformation, font=askRedditFont, fill=(150, 150, 150))

    #adjust spacing as needed
    for i in range(len(lines)):
        d.text((150, (250 + (i * 100))), lines[i], font=questionFont, fill=(0))
        slides.append(img.copy())

    #Create frames based on time it takes for TTS to speak
    frames = []
    for i in range(len(lines)):
        subQuestionIndex = 0
        while os.path.isfile('{0}clips/subQuestion{1}.wav'.format(homePath, subQuestionIndex)):
            subQuestionIndex = subQuestionIndex + 1
        path = '{0}clips/subQuestion{1}.wav'.format(homePath, subQuestionIndex)
        voice.create_recording(path, lines[i])
        f = sf.SoundFile(path)
        seconds = ((len(f) / f.samplerate))-0.6

        slides[i].save("{0}clips/q{1}.png".format(homePath, i))
        if(i == len(lines)-1):
            frame = ImageClip('{0}clips/q{1}.png'.format(homePath, i)).set_duration(seconds+2)
        else:
            frame = ImageClip('{0}clips/q{1}.png'.format(homePath, i)).set_duration(seconds)
        frames.append(frame)
    subQuestionIndex = len(lines)

    #Assemble the frames
    myMovie = concatenate_videoclips(frames, method="compose")
    for frame in frames:
        frame.close()
        del frame
    questionIndex = 0
    while os.path.isfile('{0}clips/question{1}.wav'.format(homePath, questionIndex)):
        questionIndex = questionIndex + 1
    audioPath = '{0}clips/question{1}.wav'.format(homePath, questionIndex)
    voice.create_recording(audioPath, question)
    time.sleep(1)


    #Create sound for buffer image
    f = sf.SoundFile(audioPath)
    seconds = ((len(f) / f.samplerate))
    sound = AudioSegment.from_wav(audioPath)
    sound += AudioSegment.silent(duration=1000)
    sound += AudioSegment.from_wav("{0}content\\beep.wav".format(homePath))
    sound.export(audioPath, format="wav")

    #Save movie to local
    questionIndex = 0
    while os.path.isfile('{0}clips/movies/movie{1}.avi'.format(homePath, questionIndex)):
        questionIndex = questionIndex + 1
    path = '{0}clips/movies/movie{1}.avi'.format(homePath, questionIndex)
    static = createStatic(0.5)
    myMovie = concatenate_videoclips([myMovie, static], method="compose")

    #Write the movie to file if possible
    try:
        myMovie.write_videofile(path, audio=audioPath, temp_audiofile='{0}/tmp/tmp.mp3'.format(homePath), codec='png', fps=10)
        close_clip(myMovie)
        static.close()
        del myMovie
        gc.collect()
    #For some reason couldn't find some tmp files, usually not a problem
    except(FileNotFoundError):
        print("couldn't delete tmp file, no big deal...")
        close_clip(myMovie)


#Create a transistion screen for a certain number of seconds
def createStatic(myDuration):
    img = Image.new("RGB", (1920, 1080), color='white')
    d = ImageDraw.Draw(img)
    for y in range(9):
        color = (randint(0,255), randint(0, 255), randint(0, 255))
        d.rectangle(((216*y, 0), ((216*(y+1)), 1080)), fill=(color))
    img.save("{0}clips/static{1}.png".format(homePath, 0))
    f = sf.SoundFile("{0}content/beep.wav".format(homePath))
    seconds = ((len(f) / f.samplerate))
    frame = ImageClip('{0}clips/static{1}.png'.format(homePath, 0)).set_duration(myDuration)

    return frame

#method to convert int to human readable format
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

#Method to close clip to conserve memory
def close_clip(vidya_clip):
    try:
        vidya_clip.reader.close()
        del vidya_clip.reader
        if vidya_clip.audio is not None:
            vidya_clip.audio.reader.close_proc()
            del vidya_clip.audio
            print("destroyed audio")
        del vidya_clip
    except Exception:
        pass

#Main method for compiling
def createCompile():
    #Create the reddit instance. NOTE: FILL IN WITH YOUR INFO FROM REDDIT API
    reddit = praw.Reddit(client_id= "",
                        client_secret = "",
                        username="",
                        password="",
                        user_agent="")

    #Make sure submission fits and is an actual Showerthought
    for submission in reddit.subreddit('showerthoughts').hot(limit=NUMBER_OF_THOTS):
        if len(submission.title) < 155 and not 'What Is A Showerthought?' in submission.title:
            if not 'The Quintessential Showerthought' in submission.title:
                makeTitleClips(
                    "showerthoughts", str(submission.author), submission.title, human_format(submission.num_comments), human_format(submission.score)
                )



#Create the video
createCompile()

#compile all the individual showerthoughts into 1 neat video
questionIndex = 0
frames = []
while os.path.isfile('{0}clips/movies/movie{1}.avi'.format(homePath, questionIndex)):
    frames.append(VideoFileClip('{0}clips/movies/movie{1}.avi'.format(homePath, questionIndex)))
    questionIndex = questionIndex + 1
video = concatenate_videoclips(frames, method="compose")


#Loop the background music
movieSeconds = video.duration
f = sf.SoundFile("{0}content/song.wav".format(homePath))
seconds = ((len(f) / f.samplerate))
sound = AudioSegment.from_wav("{0}content/song.wav".format(homePath))
repeat = int(movieSeconds/seconds)+1
repeat = min(5, repeat)
for i in range(repeat):
    sound += sound

#Export the looped audio and assign to the video
sound.export("{0}content/song2.wav".format(homePath), format="wav")
audioClip = AudioFileClip("{0}content/song2.wav".format(homePath))
video = video.set_audio(CompositeAudioClip([audioClip, video.audio])).set_duration(movieSeconds)

#Dump the video
path = ''
try:
    questionIndex = 0
    while os.path.isfile("{0}movies/movie{1}.mp4".format(homePath, questionIndex)):
        questionIndex = questionIndex + 1
    path = "{0}movies/movie{1}.mp4".format(homePath, questionIndex)
    video.write_videofile(path,  temp_audiofile='{0}movies/tmp/tmp.mp3'.format(homePath), codec='png', fps=10)

except(FileNotFoundError):
    print("couldn't delete tmp file, no big deal...")

#Clear the memory
for frame in frames:
    frame.close()

#Method to create metadata for youtube video
def assembleMetaData(number):
    titleString = 'r/Showerthoughts Top Posts Of The Day Compilation #{0}'.format(number)
    descriptionString = """Your Daily Dose of Reddit Showerthoughts. According to /r/showerthoughts,
    'a showerthought is a miniature epiphany that makes the mundane more
    interesting'. If you enjoyed this content, be sure to subscribe,
    and check out reddit.com/r/Showerthoughts"""

    dict = {
    'title':titleString,
    'description':descriptionString,
    'tags':['Reddit', 'showerthoughts', 'epiphany', 'subreddit', 'comedy', 'posts', 'stories', 'thinking'],
    'privacyStatus':'private',
    'category':'23'
    }

    with open('{0}data.json'.format(homePath), 'w') as fp:
        json.dump(dict, fp, sort_keys=True, indent=4)


#Run the OS command that will upload to youtube
assembleMetaData(questionIndex)
cmd = '{0}youtubeuploader.exe -filename {0}movies/movie{1}.mp4 -metaJSON {0}data.json'.format(homePath, questionIndex)
print("attempting to upload")
os.chdir(homePath)
os.system(cmd)

#Clean up the mess we made
folder = '{0}/clips'.format(homePath)
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)
folder = '{0}/clips/movies'.format(homePath)
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)




print("program ended :)")
