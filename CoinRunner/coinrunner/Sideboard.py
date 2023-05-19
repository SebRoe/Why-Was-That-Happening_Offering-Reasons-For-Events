import pygame, random 
from pygame.locals import *
from pygame.math import Vector2
from .constants import * 
from .utils import *
import numpy as np 


class Sideboard(pygame.sprite.Sprite):

    def __init__(self):

        super(Sideboard, self).__init__()
        self.surf = pygame.Surface((SIDE_WIDTH, SIDE_HEIGHT))
        self.bg_color = (50,50,50)
        self.txt_color = (255, 255, 255)
        self.surf.fill(self.bg_color)
        self.rect = self.surf.get_rect(
            center = (SCREEN_WIDTH - SIDE_WIDTH/2, SCREEN_HEIGHT/2)
        )

        self.fontHeader = pygame.font.Font(PATH_FONT, 25)
        self.fontText = pygame.font.Font(PATH_FONT, 20) 

        self.colorOk = (0, 255, 0)
        self.colorWarning = (255, 255, 0)

        self.texts = []


        targetFuncMapping = {
            TargetingMetric.COSINE_SIMILARITY: self.add_targetingv1,
            TargetingMetric.REDUCING_DISTANCE: self.add_targetingv2
        }


        self.add_target = targetFuncMapping[TARGETING_METRIC]


    def set_menu_text(self):
        self.surf.fill(self.bg_color)

        self.texts = []
        self.texts.append((self.fontHeader.render("- Runtime Informations -", True, self.txt_color), 20))

        for counter, text in enumerate(self.texts):
            self.surf.blit(text[0], (75, SIDE_HEIGHT // 2 ))



    def update(self, recording, current_frame):

        self.surf.fill(self.bg_color)
        statusJson = recording["status"]

        self.texts = []
        self.texts.append((self.fontHeader.render("- Status Informations -", True, self.txt_color), 35))
        self.texts.append((self.fontText.render(f"Total Frames: {statusJson['totalFrames']}", True, self.txt_color), 35))
        self.texts.append((self.fontText.render(f"Collected Powerup: {statusJson['collectedPowerUp']}", True, self.txt_color), 25))
        self.texts.append((self.fontText.render(f"Collected Coin: {statusJson['collectedCoin']}", True, self.txt_color), 25))  
        self.texts.append((self.fontText.render(f"Killed Enemy: {statusJson['killedEnemy']}", True, self.txt_color), 25))
        self.texts.append((self.fontText.render(f"Total Score: {recording['data'][current_frame]['score']}", True, self.txt_color), 25))

        marginTop = 0

        for text in self.texts:
            marginTop += text[1] 
            self.surf.blit(text[0], (20, marginTop))
            
        curr_dataJson = recording["data"][current_frame]
        

        distance_Player_Powerup, distance_Player_Goal, distance_Player_Coin, distance_Player_Enemy = None, None, None, None


        if "enemy" in curr_dataJson:
            distance_Player_Enemy = DISTANCE_METRIC.value[0](curr_dataJson["player"]["pos"], curr_dataJson["enemy"]["pos"])
        else:
            distance_Player_Enemy = 0

        if "goldcoin" in curr_dataJson:
            distance_Player_Coin = DISTANCE_METRIC.value[0](curr_dataJson["player"]["pos"], curr_dataJson["goldcoin"]["pos"])
        else:
            distance_Player_Coin = 0

        if "powerup" in curr_dataJson:
            distance_Player_Powerup = DISTANCE_METRIC.value[0](curr_dataJson["player"]["pos"], curr_dataJson["powerup"]["pos"])
        else:
            distance_Player_Powerup = 0

        if "goal" in curr_dataJson:
            distance_Player_Goal = DISTANCE_METRIC.value[0](curr_dataJson["player"]["pos"], curr_dataJson["goal"]["pos"])
        else:
            distance_Player_Goal = 0


        if "enemy" in curr_dataJson and "goal" in curr_dataJson:
            distance_Enemy2Goal = DISTANCE_METRIC.value[0](curr_dataJson["enemy"]["pos"], curr_dataJson["goal"]["pos"])
        else:
            distance_Enemy2Goal = 0

        if "powerup" in curr_dataJson and "goal" in curr_dataJson:
            distance_Powerup2Goal = DISTANCE_METRIC.value[0](curr_dataJson["powerup"]["pos"], curr_dataJson["goal"]["pos"])
        else:
            distance_Powerup2Goal = 0


        if "powerup" in curr_dataJson and "enemy" in curr_dataJson:
            distance_Powerup2Enemy = DISTANCE_METRIC.value[0](curr_dataJson["powerup"]["pos"], curr_dataJson["enemy"]["pos"])
        else:
            distance_Powerup2Enemy = 0


        if "goldcoin" in curr_dataJson and "goal" in curr_dataJson:
            distance_Coin2Goal = DISTANCE_METRIC.value[0](curr_dataJson["goldcoin"]["pos"], curr_dataJson["goal"]["pos"])
        else:
            distance_Coin2Goal = 0


        if "goldcoin" in curr_dataJson and "enemy" in curr_dataJson:
            distance_Coin2Enemy = DISTANCE_METRIC.value[0](curr_dataJson["goldcoin"]["pos"], curr_dataJson["enemy"]["pos"])
        else:
            distance_Coin2Enemy = 0

        if "goldcoin" in curr_dataJson and "powerup" in curr_dataJson:
            distance_Coin2Powerup = DISTANCE_METRIC.value[0](curr_dataJson["goldcoin"]["pos"], curr_dataJson["powerup"]["pos"])
        else:
            distance_Coin2Powerup = 0

        if "enemy" in curr_dataJson and "goldcoin" in curr_dataJson:
            distance_Enemy2Coin = DISTANCE_METRIC.value[0](curr_dataJson["enemy"]["pos"], curr_dataJson["goldcoin"]["pos"])
        else:
            distance_Enemy2Coin = 0
        

        self.texts_distances = []
        self.texts_distances.append((self.fontHeader.render(f"- {DISTANCE_METRIC.value[1]} Informations -", True, self.txt_color), 50))
        self.texts_distances.append((self.fontText.render(f"Distance Player - Enemy: {distance_Player_Enemy}", True, self.txt_color), 35))
        self.texts_distances.append((self.fontText.render(f"Distance Player - Coin: {distance_Player_Coin}", True, self.txt_color), 25))
        self.texts_distances.append((self.fontText.render(f"Distance Player - Powerup: {distance_Player_Powerup}", True, self.txt_color), 25))
        self.texts_distances.append((self.fontText.render(f"Distance Player - Goal: {distance_Player_Goal}", True, self.txt_color), 25))


        for text in self.texts_distances:
            marginTop += text[1] 
            self.surf.blit(text[0], (20, marginTop))


        recording["data"][current_frame]["distances"] = {
            "enemy": distance_Player_Enemy,
            "goldcoin": distance_Player_Coin,
            "powerup": distance_Player_Powerup,
            "goal": distance_Player_Goal,

            "enemy2goal": distance_Enemy2Goal,
            "enemy2coin": distance_Enemy2Coin,

            "powerup2goal": distance_Powerup2Goal,
            "powerup2enemy": distance_Powerup2Enemy,

            "coin2goal": distance_Coin2Goal, 
            "coin2enemy": distance_Coin2Enemy,
            "coin2powerup": distance_Coin2Powerup
        }

        recording = self.add_target(recording, marginTop, current_frame)

        return recording



    def add_targetingv1(self, recording, marginTop, current_frame):

        def myCos(a, b):
            if b is not None:
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            else:
                return -1 

        uniqueFrames = reduceInformationsToUserInput(recording) 
        self.texts_targeting = []
        self.texts_targeting.append((self.fontHeader.render(f"- Targeting Informations -", True, self.txt_color), 50))
        targetingCoin, targetingPowerup, targetingGoal, targetingEnemy = False, False, False, False
        
        if len(uniqueFrames) > 1:

            # Targeting Informations 
            currentFrame = uniqueFrames[-1]
            secondToLastFrame = uniqueFrames[-2]

            movement = np.array(currentFrame["player"]["pos"]) - np.array(secondToLastFrame["player"]["pos"])

            p2Enemy = np.array(currentFrame["enemy"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "enemy" in currentFrame else None
            p2Coin = np.array(currentFrame["goldcoin"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "goldcoin" in currentFrame else None
            p2Powerup = np.array(currentFrame["powerup"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "powerup" in currentFrame else None
            p2Goal = np.array(currentFrame["goal"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "goal" in currentFrame else None

            cosEnemy = myCos(movement, p2Enemy)
            cosCoin = myCos(movement, p2Coin)
            cosPowerup = myCos(movement, p2Powerup)
            cosGoal = myCos(movement, p2Goal)

            max = np.array([cosEnemy, cosCoin, cosPowerup, cosGoal]).max()

            if max == cosEnemy:
                targetingEnemy = True
            elif max == cosCoin:
                targetingCoin = True
            elif max == cosPowerup:
                targetingPowerup = True
            elif max == cosGoal:
                targetingGoal = True





        elif len(uniqueFrames) == 1:
            currentFrame = uniqueFrames[0]

            movement = np.array(currentFrame["player"]["pos"]) - np.array(recording["data"][1]["player"]["pos"])

            p2Enemy = np.array(currentFrame["enemy"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "enemy" in currentFrame else None
            p2Coin = np.array(currentFrame["goldcoin"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "goldcoin" in currentFrame else None
            p2Powerup = np.array(currentFrame["powerup"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "powerup" in currentFrame else None
            p2Goal = np.array(currentFrame["goal"]["pos"]) - np.array(currentFrame["player"]["pos"]) if "goal" in currentFrame else None

            cosEnemy = myCos(movement, p2Enemy)
            cosCoin = myCos(movement, p2Coin)
            cosPowerup = myCos(movement, p2Powerup)
            cosGoal = myCos(movement, p2Goal)

            max = np.array([cosEnemy, cosCoin, cosPowerup, cosGoal]).max()

            if max == cosEnemy:
                targetingEnemy = True
            elif max == cosCoin:
                targetingCoin = True
            elif max == cosPowerup:
                targetingPowerup = True
            elif max == cosGoal:
                targetingGoal = True


        recording["data"][current_frame]["targeting"] = {
            "enemy": targetingEnemy,
            "goldcoin": targetingCoin,
            "powerup": targetingPowerup,
            "goal": targetingGoal
        }


        self.texts_targeting.append((self.fontText.render(f"Targeting Enemy: {targetingEnemy}", True, self.txt_color), 35))
        self.texts_targeting.append((self.fontText.render(f"Targeting Coin: {targetingCoin}", True, self.txt_color), 25))
        self.texts_targeting.append((self.fontText.render(f"Targeting Powerup: {targetingPowerup}", True, self.txt_color), 25))
        self.texts_targeting.append((self.fontText.render(f"Targeting Goal: {targetingGoal}", True, self.txt_color), 25))

        for text in self.texts_targeting:
            marginTop += text[1] 
            self.surf.blit(text[0], (20, marginTop))


        return recording



    def add_targetingv2(self, recording, marginTop, current_frame):

        def myCos(a, b):
            if b is not None:
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            else:
                return -1 

        uniqueFrames = reduceInformationsToUserInput(recording) 
        self.texts_targeting = []
        self.texts_targeting.append((self.fontHeader.render(f"- Targeting Informations -", True, self.txt_color), 50))
        targetingCoin, targetingPowerup, targetingGoal, targetingEnemy = False, False, False, False
        
        if len(uniqueFrames) > 1:
            # Targeting Informations 

            currentFrame = uniqueFrames[-1]
            secondToLastFrame = uniqueFrames[-2]

            if currentFrame["distances"]["enemy"] is not None and secondToLastFrame["distances"]["enemy"] is not None:
                targetingEnemy = True if currentFrame["distances"]["enemy"] < secondToLastFrame["distances"]["enemy"] else False

            if currentFrame["distances"]["goldcoin"] is not None and secondToLastFrame["distances"]["goldcoin"] is not None:
                targetingCoin = True if currentFrame["distances"]["goldcoin"] < secondToLastFrame["distances"]["goldcoin"] else False
            
            if currentFrame["distances"]["powerup"] is not None and secondToLastFrame["distances"]["powerup"] is not None:
                targetingPowerup = True if currentFrame["distances"]["powerup"] < secondToLastFrame["distances"]["powerup"] else False
            
            if currentFrame["distances"]["goal"] is not None and secondToLastFrame["distances"]["goal"] is not None:
                targetingGoal = True if currentFrame["distances"]["goal"] < secondToLastFrame["distances"]["goal"] else False

        
        elif len(uniqueFrames) == 1:
            currentFrame = uniqueFrames[0]

            start_player_enemy = DISTANCE_METRIC.value[0](recording["data"][1]["player"]["pos"], recording["data"][1]["enemy"]["pos"])
            start_player_coin = DISTANCE_METRIC.value[0](recording["data"][1]["player"]["pos"], recording["data"][1]["goldcoin"]["pos"])
            start_player_powerup = DISTANCE_METRIC.value[0](recording["data"][1]["player"]["pos"], recording["data"][1]["powerup"]["pos"])
            start_player_goal = DISTANCE_METRIC.value[0](recording["data"][1]["player"]["pos"], recording["data"][1]["goal"]["pos"])

            targetingEnemy = True if currentFrame["distances"]["enemy"] < start_player_enemy else False
            targetingCoin = True if currentFrame["distances"]["goldcoin"] < start_player_coin else False
            targetingPowerup = True if currentFrame["distances"]["powerup"] < start_player_powerup else False
            targetingGoal = True if currentFrame["distances"]["goal"] < start_player_goal else False

        
        recording["data"][current_frame]["targeting"] = {
            "enemy": targetingEnemy,
            "goldcoin": targetingCoin,
            "powerup": targetingPowerup,
            "goal": targetingGoal
        }

        self.texts_targeting.append((self.fontText.render(f"Targeting Enemy: {targetingEnemy}", True, self.txt_color), 35))
        self.texts_targeting.append((self.fontText.render(f"Targeting Coin: {targetingCoin}", True, self.txt_color), 25))
        self.texts_targeting.append((self.fontText.render(f"Targeting Powerup: {targetingPowerup}", True, self.txt_color), 25))
        self.texts_targeting.append((self.fontText.render(f"Targeting Goal: {targetingGoal}", True, self.txt_color), 25))

        for text in self.texts_targeting:
            marginTop += text[1] 
            self.surf.blit(text[0], (20, marginTop))


        return recording