import os
# class ConfigClass:
#
#
#
#     @staticmethod
#     def set_config(corpus_path, output_path, stemming):
#         if output_path is None:
#             output_path = 'posting'
#         try:
#             if not os.path.exists(output_path):
#                 os.mkdir(output_path)
#         except:
#             if not os.path.exists('posting'):
#                 os.mkdir('posting')
#             ConfigClass.savedFileMainFolder = 'posting'
#             # raise Exception("Error in init_config before with/without adding")
#             pass
#         if stemming:
#             output_path = output_path + "/WithStem"
#             ConfigClass.savedFileMainFolder = output_path
#         else:
#             output_path = output_path + "/WithoutStem"
#             ConfigClass.savedFileMainFolder = output_path
#         try:
#             if not os.path.exists(ConfigClass.savedFileMainFolder):
#                 os.mkdir(ConfigClass.savedFileMainFolder)
#         except:
#             os.mkdir('posting')
#             ConfigClass.savedFileMainFolder = 'posting'
#             raise Exception("Error in init_config after with/without adding")
#             pass
#
#         if corpus_path is None:
#             ConfigClass.corpusPath = 'testData'
#         else:
#
#             ConfigClass.corpusPath = corpus_path
#         ConfigClass.toStem = stemming
#
#         print('Project was created successfully..')

class ConfigClass:
    savedFileMainFolder = 'C:\\Users\\liors\\Desktop\\BGU\\year3\\semestrer5\\IR\\SearchEngine_PartC\\code\\Search-Engine-PartC'
    corpusPath = None
    toStem = None
    expendedWordWeight = 0.5
    wordFromOGQueryWeight = 1
    shortQueryFactor = 1
    longQueryFactor = 0.3
    shortQueryLen = 2
    numOfDocsToRetrieve = 20000

    ##### need to sum to 1####
    cosSinWeight = 0.7
    innerProductWeight = 1 - cosSinWeight
    ##########################

    def __init__(self):
        # link to a zip file in google drive with your pretrained model
        self._model_url = None
        # False/True flag indicating whether the testing system will download
        # and overwrite the existing model files. In other words, keep this as
        # False until you update the model, submit with True to download
        # the updated model (with a valid model_url), then turn back to False
        # in subsequent submissions to avoid the slow downloading of the large
        # model file with every submission.
        self._download_model = False

        self.corpusPath = ''
        self.savedFileMainFolder = ''
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False
        self.google_news_vectors_negative300_path = '../../../../GoogleNews-vectors-negative300.bin'
        self.glove_twitter_27B_25d_path = '../../../../glove.twitter.27B.25d.txt'

        print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath

    def get_model_url(self):
        return self._model_url

    def get_download_model(self):
        return self._download_model

    @staticmethod
    def get_output():
        return ConfigClass.savedFileMainFolder