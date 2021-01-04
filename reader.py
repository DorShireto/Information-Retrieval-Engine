import os
import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name): #TODO DO NOT CHANGE THIS!!!!
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

    """
    This function will loop over self.corpus_path, which holds the corpus location.
    will return data frame
    """

    def readAllCorpus(self):

        df = []
        # TODO: might need to find a faster way then os.walk https://stackoverflow.com/questions/32455262/os-walk-very-slow-any-way-to-optimise
        for dirPath, dirNames, fileNames in os.walk(self.corpus_path):
            for file in fileNames:
                if not file.endswith('.parquet'):
                    continue
                a=dirPath.split("\\")
                if len(a) == 2 :
                    b = a[1]+"\\"+file
                    df.extend(self.read_file(b))
                else:
                    df.extend(self.read_file(file))

        return df

