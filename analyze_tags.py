import pandas as pd
import os
import json
import praw
from local_secrets import REDDIT_SECRET, REDDIT_CLIENT_ID, REDDIT_USER_AGENT

aggregated_tags_path = "filtered_subreddits_flattened"
aggregated_tags_filename = "aggregated_tags.csv"

# set up reddit client app
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# creates the aggregated tags csv file
def make_aggregated_tags():
    all_tags = set()
    tags_dict = {}
    tags_directory = os.path.join(aggregated_tags_path, ".ts")
    filenames = os.listdir(tags_directory)
    for filename in filenames:
        if filename.split(".")[-1] != "json" or filename == "tsi.json":
            continue

        image_name = '.'.join(filename.split(".")[:-1])

        # get all of the tags associated with this file and add them to tags_dict
        with open(os.path.join(tags_directory, filename), "r", encoding="utf-8-sig") as f:
            tag_json = json.load(f)

            tags = []
            for tag in tag_json["tags"]:
                tags.append(tag["title"])

            for tag in tags:
                all_tags.add(tag)

            tags_dict[image_name] = tags

    # convert to a dataframe and write as a csv
    flattened_dict = []
    for image_name, tags in tags_dict.items():
        record_dict = {}
        record_dict["image_name"] = image_name
        for tag in all_tags:
            if tag in tags:
                record_dict[tag] = True
            else:
                record_dict[tag] = False
        flattened_dict.append(record_dict)

    df = pd.DataFrame(flattened_dict)
    df.to_csv(os.path.join(aggregated_tags_path, aggregated_tags_filename))

def do_analysis():
    # open up the aggregated tags csv
    aggregated_tags_csv = os.path.join(aggregated_tags_path, aggregated_tags_filename)
    with open(aggregated_tags_csv, "r") as f:
        raw_tags_df = pd.read_csv(f)
        raw_tags_df.pop("Unnamed: 0")

    # aggregate the total number of each tag
    raw_tags_df.loc["total"] = raw_tags_df.sum(numeric_only=True)
    print("TAG COUNTS:")
    print(raw_tags_df.loc["total"])
    print("\n")

    # get the subreddits of each image
    if not os.path.isfile("merged_metadata.csv"):
        image_metadata_df = pd.read_json("image_metadata.json").transpose()
        image_metadata_df["image_name"] = image_metadata_df.index
        merged_metadata_df = pd.merge(raw_tags_df, image_metadata_df, on="image_name", how="left")
        merged_metadata_df["subreddit_name"] = merged_metadata_df["post_id"].map(get_subreddit)
        merged_metadata_df.to_csv("merged_metadata.csv")

    merged_metadata_df = pd.read_csv("merged_metadata.csv")
    merged_metadata_df.pop("Unnamed: 0")

    # aggregate number of posts per subreddit
    groupedby_subreddit_df = merged_metadata_df.drop(["image_name", "url", "post_id"], axis=1)
    groupedby_subreddit_df = groupedby_subreddit_df.replace({"False": 0, "True": 1})
    groupedby_subreddit_df = groupedby_subreddit_df.groupby("subreddit_name").sum()
    columns_no_none = list(groupedby_subreddit_df.columns)
    columns_no_none.remove("none")
    groupedby_subreddit_df["total_tags"] = groupedby_subreddit_df.sum(axis=1)
    groupedby_subreddit_df["not_none_tags"] = groupedby_subreddit_df[columns_no_none].sum(axis=1)
    groupedby_subreddit_df["percent_not_none"] = 100 * groupedby_subreddit_df["not_none_tags"] / groupedby_subreddit_df["total_tags"]
    groupedby_subreddit_df.loc["total"] = groupedby_subreddit_df.sum()
    print("SUBREDDIT COUNTS:")
    print(groupedby_subreddit_df)
    print("\n")
    groupedby_subreddit_df.to_csv("subreddits_analysis.csv")


def get_subreddit(post_id):
    print(post_id)
    try:
        submission = reddit.submission(post_id)
        return str(submission.subreddit)
    except:
        return None

def main():
    # create the aggregated tags csv if needed
    aggregated_tags_csv = os.path.join(aggregated_tags_path, aggregated_tags_filename)
    if not os.path.isfile(aggregated_tags_csv):
        make_aggregated_tags()

    do_analysis()    

if __name__ == "__main__":
    main()