from .preprocessing import preprocess_dir, list_dirs_preprocessed 


def process_data(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG,  save, settings):
    preprocess_dir(DIRPATH, TAG, PREPROTAG, REDUCTIONTAG, save=save, settings=settings)
    return list_dirs_preprocessed(DIRPATH, PREPROTAG, REDUCTIONTAG, settings=settings)


def check_sanity(TAG, PREPROTAG, REDUCTIONTAG, DIRPATH):

    num_preprocessedDirs = len(list_dirs_preprocessed(DIRPATH, PREPROTAG, REDUCTIONTAG))
    print("Found preprocessed dirs: ", num_preprocessedDirs)

    if num_preprocessedDirs < 1:
        raise Exception("No preprocessed dirs found")
