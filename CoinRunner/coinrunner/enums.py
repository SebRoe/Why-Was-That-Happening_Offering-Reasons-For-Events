import enum 



class Positioning(enum.Enum):
    ALL_RANDOM = 0, "All random"
    ALL_FIXED = 2, "All fixed"  



class DistanceMetric(enum.Enum):
    MANHATTEN = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1]), "Manhatten Distance"
    EUCLIDEAN = lambda x, y: ((x[0] - y[0])**2 + (x[1] - y[1])**2)**0.5, "Euclidean Distance"


class TargetingMetric(enum.Enum):
    COSINE_SIMILARITY = 0, "Cosine Similarity"
    REDUCING_DISTANCE = 1, "Reducing Distance"