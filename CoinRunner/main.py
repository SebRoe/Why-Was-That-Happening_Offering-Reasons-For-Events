
import os 

SHOW_WINDOW = True
if not SHOW_WINDOW:
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

from coinrunner.CoinRunner import CoinRunner 
from setup_utils import * 
import random 

random.seed()
TAG = RecordingTag.RANDOM

def main():
    path = setup_directory(TAG)
    game = CoinRunner(path, TAG, useAgent=False, max_runs=500, window=SHOW_WINDOW, savescreens=False)


if __name__ == "__main__":
    main() 