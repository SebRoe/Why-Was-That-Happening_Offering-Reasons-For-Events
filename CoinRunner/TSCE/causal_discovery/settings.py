import sys, os 
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ))
from constants import *

TAG = RecordingTag.KILLER5.value[1]
DIRPATH = os.path.join("recordings", TAG, "data")
PREPROTAG = PreprocessingTag.V17
REDUCTIONTAG = ReducingTag.NOTHING

equal_settings = {

    "POSITIONING" : Positioning.ALL_RANDOM.value[1],
    "DISTANCE_METRIC" : DistanceMetric.MANHATTEN.value[1],
    "TARGETING_METRIC" : TargetingMetric.COSINE_SIMILARITY.value[1],
    "ENEMY_MOVING" : False,
    "EXISTENCE_GOLDCOIN" : 0.5, # Alt: 0.75, 1
    "EXISTENCE_ENEMY" : 0.75, # Alt: 0.75, 1
    "EXISTENCE_POWERUP" : 0.75, # Alt: 0.75, 1
}


USE_ROLLOUT_UNTIL = 500 