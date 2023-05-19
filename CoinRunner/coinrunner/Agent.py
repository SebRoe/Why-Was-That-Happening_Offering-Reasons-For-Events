from TSCE.utils.enums import RecordingTag
from pygame.locals import *
import random
from numpy.random import choice
from bisect import bisect

class Agent():

    def __init__(self, recordingTag, max_runs):
        
        self.behave = {
            RecordingTag.COINCOLLECTOR: self.behave_coincollector,
            RecordingTag.RANDOM: self.behave_random,
            RecordingTag.MAXOUT: self.behave_maxout,
            RecordingTag.KILLER: self.behave_killer,
            RecordingTag.KILLER2: self.behave_killer,
            RecordingTag.KILLER3: self.behave_killer,   
            RecordingTag.KILLER4: self.behave_killer,
            RecordingTag.KILLER5: self.behave_killer,
        }

        self.behaviour = self.behave[recordingTag]
        self.max_runs = max_runs

        if recordingTag == RecordingTag.KILLER5:
            if random.randint(0,100) > 95:
                self.makeNoise1 = True 
                print("Agent Making Noise 1")
            else:
                self.makeNoise1 = False 
        else:
            self.makeNoise1 = False


        if recordingTag == RecordingTag.KILLER5:
            if random.randint(0,100) > 95:
                self.makeNoise2 = True 
                print("Agent Making Noise 2")
            else:
                self.makeNoise2 = False 
        else:
            self.makeNoise2 = False



    def next(self):
        self.max_runs -= 1
        print("Runs left: ", self.max_runs)

    
    def isDone(self):

        return self.max_runs <= 0



    def walk(self, gamestate, currentframe):
        return self.behaviour(gamestate, currentframe)





    def random_walk(self, posPlayer, posObstacle, gamestate):

        if posObstacle[0] > posPlayer[0] and posObstacle[1] > posPlayer[1]:
            #return weighted_choice([([K_d], 15), ([K_s], 15), ([K_d, K_s], 70)])
            return [K_d, K_s]

        elif posObstacle[0] > posPlayer[0] and posObstacle[1] < posPlayer[1]:
            #return weighted_choice([([K_d], 15), ([K_w], 15), ([K_d, K_w], 70)])
            return [K_d, K_w]

        elif posObstacle[0] < posPlayer[0] and posObstacle[1] > posPlayer[1]:
            #return weighted_choice([([K_a], 15), ([K_s], 15), ([K_a, K_s], 70)])
            return [K_a, K_s]

        elif posObstacle[0] < posPlayer[0] and posObstacle[1] < posPlayer[1]:
            #return weighted_choice([([K_a], 15), ([K_w], 15), ([K_a, K_w], 70)])
            return [K_a, K_w]

        elif posObstacle[0] > posPlayer[0]:
            return [K_d]

        elif posObstacle[0] < posPlayer[0]:
            return [K_a]

        elif posObstacle[1] > posPlayer[1]:
            return [K_s]

        elif posObstacle[1] < posPlayer[1]:
            return [K_w]



    def behave_coincollector(self, gamestate, currentframe):

        if "goldcoin" in gamestate["data"][currentframe - 1 ]:
            goldcoin_pos = gamestate["data"][currentframe - 1]["goldcoin"]["pos"]
            player_pos = gamestate["data"][currentframe - 1]["player"]["pos"]
            return self.random_walk(player_pos, goldcoin_pos, gamestate)
        else:
            goal_pos = gamestate["data"][currentframe - 1]["goal"]["pos"]
            player_pos = gamestate["data"][currentframe - 1]["player"]["pos"]
            return self.random_walk(player_pos, goal_pos, gamestate)




    def behave_random(self, gamestate, currentframe):
        pass


    def behave_maxout(self, gamestate, currentframe):
        pass


    def behave_killer(self, gamestate, currentframe):
        


        if "powerup" in gamestate["data"][currentframe - 1 ] and "enemy" in gamestate["data"][currentframe - 1]:
            if self.makeNoise1:
                powerup_pos = gamestate["data"][currentframe - 1]["enemy"]["pos"]
                player_pos = gamestate["data"][currentframe - 1]["player"]["pos"] 
            else:
                powerup_pos = gamestate["data"][currentframe - 1]["powerup"]["pos"]
                player_pos = gamestate["data"][currentframe - 1]["player"]["pos"]
            return self.random_walk(player_pos, powerup_pos, gamestate)

        elif "enemy" in gamestate["data"][currentframe - 1 ] and gamestate["data"][currentframe - 1]["player"]["collectedPowerUp"]:
            if self.makeNoise2:
                enemy_pos = gamestate["data"][currentframe - 1]["goal"]["pos"]
                player_pos = gamestate["data"][currentframe - 1]["player"]["pos"]
            else:
                enemy_pos = gamestate["data"][currentframe - 1]["enemy"]["pos"]
                player_pos = gamestate["data"][currentframe - 1]["player"]["pos"]
            return self.random_walk(player_pos, enemy_pos, gamestate)

        else:
            goal_pos = gamestate["data"][currentframe - 1]["goal"]["pos"]
            player_pos = gamestate["data"][currentframe - 1]["player"]["pos"]
            return self.random_walk(player_pos, goal_pos, gamestate)




class FakeEvent():

    def __init__(self, type, key):
        self.type = type
        self.key = key


def weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random() * total
    i = bisect(cum_weights, x)
    return values[i]