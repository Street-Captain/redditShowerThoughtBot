# Reddit ShowerThoughtBot For Youtube
This program scraps data from reddit using the reddit api, and uploads it to youtube. I have been running a channel that executes this script at 3:00 AM everyday. You can find it at https://www.youtube.com/channel/UCQPCWqI94BfdV26Qamp2JGA

The program will scrap the reddit api and optain the top shower thoughts of the day. It will then take those posts and compile them into images. It will also compile those posts into audio files. Between posts, a buffer image will show. After all the posts have been compiled into images with their corresponding audio segments, background music will be added. The video will then be uploaded to youtube. 

# Installation
First, you will need to install some dependencies...

```
pip install moviepy
pip install pillow
pip install praw
pip install soundfile
pip install tts.sapi
pip install librosa
pip install gc
pip install os
```

In the cloned directory, you will need to import the fonts you would like to use, and put them in the "font" directory. You will also need to go to https://github.com/porjo/youtubeuploader to download the youtube uploader pre-compiled binary. Place the .exe file in the main directory downloaded from github.

Next, you will need to change some of the code.

On line 25, you will see a line
```
voice.set_voice(voice.get_voices()[0])
```
If you would like to have Daniel (UK) narrate your videos, go to https://harposoftware.com/en/ and download the voice. Then change the line to
```
voice.set_voice(voice.get_voices()[2])
```
You will also need to change the home path variable on line 28
```
homePath = "Path/to/directory"
```

You will need to fill in the reddit api object with your information line 199
```
    reddit = praw.Reddit(client_id= "",
                        client_secret = "",
                        username="",
                        password="",
                        user_agent="")
```
If you aren't entirely sure how to fill this in, check out https://praw.readthedocs.io/en/latest/


In the assembleMetaData method, (line 259) you will find this:
```
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
 ```
 
Change this to fit your needs. You can leave it as it is and it will work fine. Change the line
```
'privacyStatus':'private',
```

# Running

To execute, run the python script by typing into the terminal
```
python redditBot.py
```

That should do it! This program takes a long time to run, so be patient. The first time it runs, it will redirect you toward a browser to have you sign into your youtube account. You only will need to do this once.

