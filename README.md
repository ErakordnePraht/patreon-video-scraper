# patreon-video-scraper
Just a quick script I wrote to download some videos from Patreon that I wanted to watch locally. Does not work with Youtube videos and might not work with some others, but it worked with what I needed so I don't really care. 

If you need to download youtube videos as well it should be easy enough to add, you'll just need to get the videos youtube link and use yt-dlp to download it instead of ffmpeg.

## Prerequisites
* You'll need chromedriver in your PATH (e.g. /usr/local/bin/) or in your project folder. I tried Firefox first, but I didn't find an option for logging network traffic for Firefox, it might be possible, I didn't search for very long.
* ffmpeg is required for combining the m3u8 playlist into an mp4 file.
* Python and everything in requirements.txt

## Usage
Create a videos/ folder in your projects directory, that is where your downloaded videos will go. The script might crash if you don't have one.

When you start the script it will ask you for your patreon session_id, this is so you can download videos that require a membership. If you're only downloading public videos you can leave this empty or insert a random string.

Next it will ask you for a link, you'll need to insert a /posts/ link or a /posts?filters[tag] or similar, the script will not work if you just insert a patreon.com/creatorname/ link unless you're a patron.

After all of that the script will open up chrome and start scraping for videos, first it will find all the posts and after that go through them one at a time.
