# CSC 544 Final Project

Created by: Drew Scott

### Summary:

This project's goal is to identify misleading data visualizations in the sports media domain. Obviously, to do so, such visualizations must be collected. This repo is where such visualizations are collected. Here, we collect visualizations from various subreddits.

### Files:
* reddit_posts.py -- utilizes the Reddit API to retreive images associated with posts from various sports related subreddits
* /subreddits -- contains directories corresponding to all the the subreddits that were accessed through the Reddit API; each sub-directory contains all of the images gathered
* /filtered_subreddits -- contains directories corresponding to all the the subreddits that were accessed through the Reddit API; each sub-directory contains images that appear to be sufficiently related to "data visualization"

### Usage

In order to run ```python3 reddit_posts.py``` to collect the data, you will have to create your own authorized Reddit application [here](https://www.reddit.com/prefs/apps). Then, create a file ```local_secrets.py``` and create the variables needed to interact with the Reddit API.
