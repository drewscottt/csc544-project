import praw
import requests
import re
from pathlib import Path
import os
import json
from local_secrets import REDDIT_SECRET, REDDIT_CLIENT_ID, REDDIT_USER_AGENT

# set up reddit client app
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# subreddits to read from
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

# track metadata for each image read
image_metadata = {}

# read all of the "Hot" posts from each subreddit
# extract the images from the posts
for subreddit_name in all_subreddits:
    print(subreddit_name)
    Path(os.path.join("subreddits", subreddit_name)).mkdir(parents=True, exist_ok=True)

    # credit: https://www.reddit.com/r/learnpython/comments/5benxs/how_do_i_download_an_image_using_praw/
    subreddit_instance = reddit.subreddit(subreddit_name)
    posts = subreddit_instance.hot(limit=None)
    for post in posts:
        # we only care about posts that are images
        if post.is_reddit_media_domain and not post.is_video:
            url = (post.url)
            file_name = url.split("/")
            if len(file_name) == 0:
                file_name = re.findall("/(.*?)", url)
            file_name = file_name[-1]
            if "." not in file_name:
                file_name += ".jpg"

            image_metadata[file_name] = {"url": post.url, "post_id": str(post)}

            image_filename = os.path.join("subreddits", subreddit_name, file_name)
            if not os.path.isfile(image_filename):
                r = requests.get(url)
                with open(image_filename, "wb") as f:
                    f.write(r.content)

# update the image_metadata.json file
with open("image_metadata.json", "r") as f:
    existing_json = json.load(f)

existing_json.update(image_metadata)

with open("image_metadata.json", "w") as f:
    json.dump(existing_json, f)
