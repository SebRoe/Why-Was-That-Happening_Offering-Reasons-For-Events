import os 
from TSCE.utils.enums import RecordingTag




def get_saving_path(tag: RecordingTag):
    path = os.path.join("recordings", tag.value[1])
    return path 



def setup_directory(tag: RecordingTag):
    path = get_saving_path(tag)
    os.makedirs(path, exist_ok=True)

    path_data = os.path.join(path, "data")
    os.makedirs(path_data, exist_ok=True)

    # path_video = os.path.join(path, "video")
    # os.makedirs(path_video, exist_ok=True)

    # path_frames = os.path.join(path, "frames", exist_ok=True)
    # os.makedirs(path_frames, exist_ok=True)
    return path_data

    
def setup_screenrecordings():
    os.makedirs("screenrecordings", exist_ok=True)



