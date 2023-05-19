import enum 

class RecordingTag(enum.Enum):
    RANDOM = (0, "random")
    COINCOLLECTOR = (1, "coincollector")
    MAXOUT = (2, "maxout") 
    KILLER = (3, "killer")
    KILLER2 = (4, "killer2")
    KILLER3 = (5, "killer3")
    KILLER4 = (6, "killer4")
    KILLER5 = (7, "killer5")

class ReducingTag(enum.Enum):
    USERINPUT = "userinput"
    NOTHING = "nothing"

class PreprocessingTag(enum.Enum):
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"
    # Check out Used Informations 
    V7 = "V7"
    # Check out Used Informations 
    V8 = "V8"
    # Check out Used Informations
    V9 = "V9"
    ## Version constructed in Miro Board
    V10 = "V10"
    ## Version constructed after Miro Board 
    V11 = "V11"
    ##
    V12 = "V12"
    V13 = "V13"
    V14 = "V14"
    V15 = "V15"
    V16 = "V16"
    V17 = "V17"

class Positioning(enum.Enum):
    ALL_RANDOM = 0, "All random"
    ALL_FIXED = 2, "All fixed"  

class DistanceMetric(enum.Enum):
    MANHATTEN = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1]), "Manhatten Distance"
    EUCLIDEAN = lambda x, y: ((x[0] - y[0])**2 + (x[1] - y[1])**2)**0.5, "Euclidean Distance"

class TargetingMetric(enum.Enum):
    COSINE_SIMILARITY = 0, "Cosine Similarity"
    REDUCING_DISTANCE = 1, "Reducing Distance"