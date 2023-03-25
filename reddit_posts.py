import praw
import requests
import re
from pathlib import Path
import os
from local_secrets import REDDIT_SECRET, REDDIT_CLIENT_ID, REDDIT_USER_AGENT

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

sports_subreddits = [
    "CollegeBasketball",
    "baseball",
    "nba",
    "nhl",
    "CFB",
    "nfl",
    "soccer"
]

teams_subreddits = [
    "Lakers",
    "bostonceltics",
    "NYYankees",
    "Dodgers",
    "KansasCityChiefs",
    "cowboys",
    "realmadrid",
    "ManchesterUnited"
]

all_subreddits = [*sports_subreddits, *teams_subreddits]

for subreddit_name in teams_subreddits:
    Path(os.path.join("subreddits", subreddit_name)).mkdir(parents=True, exist_ok=True)

    # credit: https://www.reddit.com/r/learnpython/comments/5benxs/how_do_i_download_an_image_using_praw/
    subreddit_instance = reddit.subreddit(subreddit_name)
    posts = subreddit_instance.hot(limit=None)
    for post in posts:
        if post.is_reddit_media_domain and not post.is_video:
            url = (post.url)
            file_name = url.split("/")
            if len(file_name) == 0:
                file_name = re.findall("/(.*?)", url)
            file_name = file_name[-1]
            if "." not in file_name:
                file_name += ".jpg"

            r = requests.get(url)
            with open(os.path.join("subreddits", subreddit_name, file_name), "wb") as f:
                f.write(r.content)
