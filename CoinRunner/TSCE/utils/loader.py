import os, json, pickle, time 
import seaborn as sns 
import matplotlib.pyplot as plt


# I/O Operations
def read_recordings_raw(dir_path: str, file_name: str):
    try:

        path = os.path.join(dir_path, file_name, "raw_" + file_name + ".json")
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except:
        raise Exception("Error reading file: " + file_name)


def read_recording_preprocessed(dir_path: str, file_name: str, preprocessing_tag, reduction_tag):
    path = os.path.join(dir_path, file_name, "processed_" + preprocessing_tag.value + "_" + reduction_tag.value + "_" + file_name + ".pickle")
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data 


def save_recordings_as_pickle(dir_path: str, file_name: str, data: dict, preprocessing_tag, reduction_tag):
    path = os.path.join(dir_path, file_name, "processed_" + preprocessing_tag.value + "_" + reduction_tag.value + "_" + file_name + ".pickle")
    with open(path, "wb") as f:
        pickle.dump(data, f)

def save_results(df, currPath, only_data=False, name_fig="", name_data=""):
    
    # Saving Figure without opening it 
    
    if name_fig == "":
        fig_path = os.path.join(currPath, "figure.png")
    else:
        fig_path = os.path.join(currPath, f"{name_fig}.png")

    if not only_data:
        sns.reset_orig()
        sns.set(rc={'figure.figsize':(20,20)})
        plt.clf()
        sns.heatmap(df, annot=True, linewidths=.5, linecolor="grey", cbar=True, cmap="seismic").get_figure()
        plt.savefig(fig_path)
        plt.close('all')

    # Saving Dataframe

    if name_data == "":
        data_path = os.path.join(currPath, "data.pickle")
    else:
        data_path = os.path.join(currPath, f"{name_data}.pickle")
    with open(str(data_path), "wb") as f:
        pickle.dump(df, f)



def load_results(path):
    pickle_files = [file for file in os.listdir(path) if file.endswith(".pickle")]
    if len(pickle_files) > 1:
        raise Exception("More than one pickle file in directory: " + path)

    file_name = pickle_files[0]

    with open(os.path.join(path, file_name), "rb") as f:
        df = pickle.load(f)
    return df



def saveObjects(Graph, path):

    with open(os.path.join(path, "obj1.pickle"), "wb") as f:
        pickle.dump(Graph[0], f)


    with open(os.path.join(path, "obj2.pickle"), "wb") as f:
        pickle.dump(Graph[1], f)


def saveObject(obj, name, path):
    with open(os.path.join(path, name + ".pickle"), "wb") as f:
        pickle.dump(obj, f)



def loadSingleResults(path: str, filename:str):
    dirs = os.listdir(path)
    dfs = [] 

    for dir in dirs:
        tmpFiles =  os.listdir(os.path.join(path, dir))
        for file in tmpFiles:
            if file == filename:
                with open(os.path.join(path, dir, file), "rb") as f:
                    df = pickle.load(f)
                    dfs.append(df)
    return dfs



### New GameState Idea 


def create_exp_directory(uuid):
    path = os.path.join("experiments", uuid)
    os.makedirs(path, exist_ok=True)
    return path


def create_exp_directory2(uuid):
    path = os.path.join("experiments2", uuid)
    os.makedirs(path, exist_ok=True)
    return path

def create_exp_mp_directory(uuid):
    path = os.path.join("TSCE", "experiments_mp", uuid)
    os.makedirs(path, exist_ok=True)
    return path


def saveSettings(path, settings):
    # Saving Settings to json 
    with open(os.path.join(path, "settings.json"), "w") as f:
        json.dump(settings, f, indent=4)


def saveGameState(gamestate, df, path):

    uuid = str(int(time.time()))
    new_path = os.path.join(path, uuid)
    os.makedirs(new_path, exist_ok=True)

    # Saving Settings to json 
    with open(os.path.join(new_path, "gamestate.json"), "w") as f:
        json.dump(gamestate, f, indent=4)

    # Saving Dataframe
    with open(os.path.join(new_path, "data.pickle"), "wb") as f:
        pickle.dump(df, f)

    return new_path


    