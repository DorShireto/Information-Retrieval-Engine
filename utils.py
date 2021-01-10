import pickle
import bz2


def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with bz2.BZ2File(name+'.pkl', 'wb') as f:
        pickle.dump(obj, f)

def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    try:
        with bz2.BZ2File(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        raise Exception("load_obj in utils")
