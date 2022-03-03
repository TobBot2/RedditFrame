import os
import sys

def base():
    subdir = '\\'
    if sys.platform == 'win32':
        subdir += 'Reddit Frame\\'

    return (os.path.dirname(os.getcwd()) + subdir).replace('\\', '/')