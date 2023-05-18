import pickle


def load_dataset(path):
    with open(path, 'rb') as f:
        return pickle.load(f)