import tweepy
import os
import json
import argparse

# Authentication tokens from your Twitter API
# (Censored here because they are private)
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

# Oauth
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True, retry_count = 3, retry_delay = 60)

# Function to get follower ids. Uses Cursor to handle rate limiting
def get_followers_ids(screen_name):
    followers_ids = []
    page_count = 0
    
    # Iterate through each page of 5000 followers 
    for page in tweepy.Cursor(api.followers_ids, id = screen_name, count = 5000).pages():
        followers_ids.extend(page)
        page_count += 1

    return followers_ids

# Function to get user records starting from an ego user (@param screen_name) 
# and all followers to the specific depth (@param depth) 
# and save as JSON in the specified directory (@param folder)
# This is VERY slow. Depth > 1 is not recommended
# To get a single user's record, use depth = 0
def get_user_record(screen_name, depth, folder):
    user_profile = api.get_user(screen_name)
    
    # Create user record
    user_record = {
        "screen_name": user_profile.screen_name,
        "user_id": user_profile.id,
        "num_followers": user_profile.followers_count,
        "followers_ids": get_followers_ids(screen_name)
        }
    
    # Write user record to JSON
    with open(os.path.join(str(folder), "{}.json".format(user_record["user_id"])), "w") as file:
        json.dump(user_record, file)
    
    # Recurse over followers to specified depth   
    if depth > 0:
        for follower in user_record["followers_ids"]:
            try:
                get_user_record(follower, depth - 1, folder)
            except tweepy.TweepError:
                print("Skipping protected user.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--screen_name", required = True, help = "Screen name to scrape")
    ap.add_argument("-d", "--depth", required = True, help = "Depth to search for followers of followers")
    ap.add_argument("-f", "--folder", required = True, help = "Folder to save individual JSONs into")
    
    args = vars(ap.parse_args())

    # Start with the ego user supplied by user
    screen_name = args["screen_name"]
    depth = int(args["depth"])
    folder = args["folder"]
    print("Scraping followers of {}...".format(screen_name))
    
    # make directory to contain JSON records
    try:
        os.makedirs(folder) ## change to fit Python 2.7
    except:
        pass
    
    get_user_record(screen_name, depth, folder)
    
    