import os


class ConfigClass:
    savedFileMainFolder = ''
    corpusPath = None
    toStem = None

    @staticmethod
    def set_config(corpus_path, output_path, stemming):
        if output_path is None:
            output_path = 'posting'
        try:
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        except:
            if not os.path.exists('posting'):
                os.mkdir('posting')
            ConfigClass.savedFileMainFolder = 'posting'
            # raise Exception("Error in init_config before with/without adding")
            pass
        if stemming:
            output_path = output_path + "/WithStem"
            ConfigClass.savedFileMainFolder = output_path
        else:
            output_path = output_path + "/WithoutStem"
            ConfigClass.savedFileMainFolder = output_path
        try:
            if not os.path.exists(ConfigClass.savedFileMainFolder):
                os.mkdir(ConfigClass.savedFileMainFolder)
        except:
            os.mkdir('posting')
            ConfigClass.savedFileMainFolder = 'posting'
            raise Exception("Error in init_config after with/without adding")
            pass

        if corpus_path is None:
            ConfigClass.corpusPath = 'testData'
        else:

            ConfigClass.corpusPath = corpus_path
        ConfigClass.toStem = stemming

        print('Project was created successfully..')

    @staticmethod
    def get_output():
        return ConfigClass.savedFileMainFolder
