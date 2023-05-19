import json, time  
import networkx as nx
import pandas as pd
import seaborn as sns
import numpy as np 
from tqdm import tqdm
import matplotlib.pyplot as plt

from IPython.display import display

from utils.preprocessing import * 
from utils.loader import *
from utils.enums import * 
from utils.plotHelper import * 
from utils.sanity import * 
from utils.postPreprocessing import *
from utils.aggregation import *
import multiprocessing as mp
from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception


TAG = RecordingTag.KILLER2.value[1]
PREPROTAG = PreprocessingTag.V7
REDUCTIONTAG = ReducingTag.NOTHING

equal_settings = {

    "POSITIONING" : Positioning.ALL_RANDOM.value[1],
    "DISTANCE_METRIC" : DistanceMetric.MANHATTEN.value[1],
    "TARGETING_METRIC" : TargetingMetric.COSINE_SIMILARITY.value[1],
    "ENEMY_MOVING" : False,
    "EXISTENCE_GOLDCOIN" : 1,
    "EXISTENCE_ENEMY" : 1,
    "EXISTENCE_POWERUP" : 1,

}

equal_settings2 = {

    "POSITIONING" : Positioning.ALL_RANDOM.value[1],
    "DISTANCE_METRIC" : DistanceMetric.MANHATTEN.value[1],
    "TARGETING_METRIC" : TargetingMetric.COSINE_SIMILARITY.value[1],
    "ENEMY_MOVING" : False,
    "EXISTENCE_GOLDCOIN" : 0.75,
    "EXISTENCE_ENEMY" : 0.75,
    "EXISTENCE_POWERUP" : 0.75,

}

DIRPATH = os.path.join("recordings", TAG, "data")



def init():
    preprocessedDirNames = process_data(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG,  save=True, settings=equal_settings)
    num_dirs = len(preprocessedDirNames)
    return preprocessedDirNames, num_dirs

def init2(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG, equal_settings):
    preprocessedDirNames = process_data(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG,  save=True, settings=equal_settings)
    num_dirs = len(preprocessedDirNames)
    return preprocessedDirNames, num_dirs

def init_ipynb(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG, equal_settings):
    preprocessedDirNames = process_data(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG,  save=True, settings=equal_settings)
    num_dirs = len(preprocessedDirNames)
    return preprocessedDirNames, num_dirs

def get_raw_data(id, preprocessedDirNames):
    return read_recording_preprocessed(DIRPATH, preprocessedDirNames[id], PREPROTAG, REDUCTIONTAG)

def get_create_saving_path(method, useUUID, *args):
    uuid = str(int(time.time()))
    if useUUID:
        path = os.path.join("TSCE","results", PREPROTAG.value, REDUCTIONTAG.value, TAG, method, *args, uuid) 
    else:
        path = os.path.join("TSCE","results", PREPROTAG.value, REDUCTIONTAG.value, TAG, method, *args)
        
    os.makedirs(path, exist_ok=True)
    return path

def get_saving_path(method, useUUID, *args):
    uuid = str(int(time.time()))
    if useUUID:
        path = os.path.join("TSCE","results", PREPROTAG.value, REDUCTIONTAG.value, TAG, method, *args, uuid) 
    else:
        path = os.path.join("TSCE","results", PREPROTAG.value, REDUCTIONTAG.value, TAG, method, *args)

    return path


    