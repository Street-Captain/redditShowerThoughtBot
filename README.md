# Reddit ShowerThoughtBot For Youtube
This program scraps data from reddit using the reddit api, and uploads it to youtube. 

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
