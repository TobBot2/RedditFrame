import os

def base():
    subdir = '\\RedditFrame\\'

    return (os.path.dirname(os.getcwd()) + subdir).replace('\\', '/')