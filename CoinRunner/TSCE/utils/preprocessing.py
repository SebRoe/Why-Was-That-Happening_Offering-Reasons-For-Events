import os
from .enums import *
from .loader import * 

def get_associated_settings(DIRPATH, settings:dict):
    fileNames = os.listdir(DIRPATH)
    associatedNames = [] 
    for fileName in fileNames:
        data = read_recordings_raw(DIRPATH, fileName)
        associated = True 
        for key, value in settings.items():
            if data["settings"][key] != value:
                associated = False
        if associated:
            associatedNames.append(fileName)
    
    return associatedNames

def list_dirs_preprocessed(dir_path: str, preprocessing_tag, reduction_tag, settings):
    dirs =get_associated_settings(dir_path, settings)
    dir_names = []
    for dir in dirs:
        for file_name in os.listdir(os.path.join(dir_path, dir)):
            if file_name.startswith("processed") and preprocessing_tag.value in file_name and reduction_tag.value in file_name:
                dir_names.append(dir)
    
    return dir_names 


def preprocess_dir(DIRPATH, tag: RecordingTag, preProTag: PreprocessingTag, reductionTag: ReducingTag, settings:dict,  save: bool = False):

    fileNames = get_associated_settings(DIRPATH, settings)
    num_files = len(fileNames)
    runs = [] 

    preprocessing = {
        PreprocessingTag.V17: preprocess_recordings_V17,
    }

    reducing = {
        ReducingTag.USERINPUT: reduce_recordings_wrt_userInput,
        ReducingTag.NOTHING: reduce_recordings_wrt_nothing
    }

    for i in range(num_files):
        used_file = fileNames[i]
        example = read_recordings_raw(DIRPATH, used_file)
        importantFrames = reducing[reductionTag](example)
        states = preprocessing[preProTag](importantFrames)

        runs.append(states)

        if save:
            save_recordings_as_pickle(DIRPATH, used_file, states, preProTag, reductionTag)

    if save:
        print("Saved preprocessed data to: ", DIRPATH)


# Preprocessing helper functions
def reduce_recordings_wrt_userInput(data: dict):
    dataJson = data["data"]
    allFrames = [] 
    for key in dataJson.keys():
        allFrames.append(dataJson[key])

    try:
        importantFrames = [] 
        for frame in allFrames:
            if frame["player"]["pressedKeys"] != []:
                importantFrames.append(frame)

            elif frame["terminated"]:
                importantFrames.append(frame)

            elif frame["collisions"]["col_playerEnemy"] or frame["collisions"]["col_playerGoldCoin"] or frame["collisions"]["col_playerPowerUp"] or frame["collisions"]["col_playerGoal"]:
                importantFrames.append(frame)
    except:
        print(json.dumps(data, indent=4))
        raise Exception("Error in reduce_recordings_wrt_userInput. Check if the data is in the correct format.")
    return importantFrames


def reduce_recordings_wrt_nothing(data: dict):
    dataJson = data["data"]
    allFrames = [] 
    for key in dataJson.keys():
        allFrames.append(dataJson[key])

    return allFrames





def preprocess_recordings_V17(frames: list):

    """This one contains also a reward variable in comparison to V11."""

    colEnemy = False 
    colGold = False 

    states = []

    finallyTerminated = False 

    for counter, frame in enumerate(frames):

        tmp = {}

        if finallyTerminated:
            #tmp["terminated"] = 1 if counter == num_important_frames - 1 or frame["collisions"]["col_playerGoal"] else 0
            tmp["terminated"] = 1
        else:
            tmp["terminated"] = 0 

        tmp["collectedPowerUp"] = 1 if frame["player"]["collectedPowerUp"] and not frame["collisions"]["col_playerPowerUp"] else 0
        tmp["collectedGoldCoin"] = 1 if frame["player"]["collectedGoldCoin"] and not frame["collisions"]["col_playerGoldCoin"] else 0
        tmp["killedEnemy"] = 1 if frame["player"]["killedEnemy"] and not frame["collisions"]["col_playerEnemy"] else 0

        tmp["collPlayerEnemy"] = 1 if frame["collisions"]["col_playerEnemy"] else 0
        tmp["collPlayerGoldcoin"] = 1 if frame["collisions"]["col_playerGoldCoin"] else 0
        tmp["collPlayerPowerup"] = 1 if frame["collisions"]["col_playerPowerUp"] else 0

        tmp["collPlayerGoal"] = 1 if frame["collisions"]["col_playerGoal"] else 0
        if tmp["collPlayerGoal"] == 1:
            finallyTerminated = True

        tmp["enemyExists"] = 1 if "enemy" in frame or frame["collisions"]["col_playerEnemy"] else 0
        tmp["goldcoinExists"] = 1 if "goldcoin" in frame or frame["collisions"]["col_playerGoldCoin"] else 0
        tmp["powerupExists"] = 1 if "powerup" in frame or frame["collisions"]["col_playerPowerUp"] else 0

        tmp["targEnemy"] = 1 if frame["targeting"]["enemy"] and ( tmp["collPlayerEnemy"] == 0 and tmp["killedEnemy"] == 0) else 0
        tmp["targGoldcoin"] = 1 if frame["targeting"]["goldcoin"] and ( tmp["collPlayerGoldcoin"] == 0 and tmp["collectedGoldCoin"]== 0) else 0
        tmp["targPowerup"] = 1 if frame["targeting"]["powerup"] and ( tmp["collPlayerPowerup"] == 0 and tmp["collectedPowerUp"]== 0) else 0
        tmp["targGoal"] = 1 if frame["targeting"]["goal"] and (tmp["collPlayerGoal"] == 0 and tmp["terminated"]== 0) else 0
    
        tmp["score"] = frame["score"]

        if frame["collisions"]["col_playerEnemy"]:
            tmp["score"] = frame["score"] - 9 if frame["score"] != -20 else -20
            colEnemy = True 

        if frame["collisions"]["col_playerGoldCoin"]:
            tmp["score"] = frame["score"] - 5
            colGold = True 

        if colEnemy or colGold:
            colEnemy = False 
            colGold = False

        states.append(tmp)

    if states[-1]["terminated"] == 0:
        tmp = {}
        for key in states[-1].keys():
            tmp[key] = states[-1][key]

        tmp["collPlayerEnemy"] = 0 
        tmp["collPlayerGoal"] = 0
        tmp["terminated"] = 1
        states.append(tmp)

    for i in range(5):
        states.append(states[-1])

    return states 

