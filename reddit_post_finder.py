from praw import Reddit
import urllib.request
from random import randint
from decouple import config

# Initialization a connection to Reddit API
reddit = Reddit(client_id=config("MY_CLIENT_ID"),
                client_secret=config("MY_CLIENT_SECRET"),
                user_agent="MY_USER_AGENT")

# How many posts can be processed in one request 
LIMIT = 100

list_of_memes_subs = ['memes', 'dankmemes', 'memes_of_the_dank']

# Gets a random post from chosen subreddit from hot
def get_random_post(sub):
    subreddit = reddit.subreddit(sub)
    posts = [post for post in subreddit.hot(limit=LIMIT)]
    random_post_number = randint(0, LIMIT - 1)
    random_post = posts[random_post_number]

    # Makes sure found post is a pic
    while random_post.url[-3:] != 'jpg':
        random_post_number = randint(0, LIMIT - 1)
        random_post = posts[random_post_number]

    return random_post


# Saves pic from found post
def save_photo(post):
    path_to_file = str(post) + ".jpg"

    img = urllib.request.urlopen(post.url).read()
    try:
        out = open(path_to_file, "wb")

    except FileNotFoundError:
        # mkdir(path_to_folder)
        out = open(path_to_file, "wb")
    out.write(img)

    return path_to_file