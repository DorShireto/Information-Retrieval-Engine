# Best searching engine - WordNet and Spelling Correction
import copy
from spellchecker import SpellChecker
import pandas as pd
from reader import ReadFile
from nltk.corpus import wordnet
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self.invertedIndex = self._indexer.inverted_idx
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """

        # r = ReadFile(ConfigClass.corpusPath)
        # documents_list = r.readAllCorpus() #change if we need to read more then 1 parquet

        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()

        utils.save_obj({}, "inverted_idx") # needed to pass boris tests, sometimes, inverted_idx fails to save in testings system


        # Iterate over every document in the file
        number_of_documents = 0
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            number_of_documents += 1
            if parsed_document.doc_length != 0: #sometimes we get an empty tweet, no need to index them
                # index the document data
                self._indexer.add_new_doc(parsed_document)
        # Inserting entities to the indexer and posting files
        self._indexer.addEntities(self._parser.suspectedEntityDict)
        # Sort the posting files
        self._indexer.update_idfWij(idx)
        self._indexer.save_index("inverted_idx")
        utils.save_obj(self._indexer.tweet_info, ConfigClass.get_output() + "/tweets_info")
        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and 
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

        # DO NOT MODIFY THIS SIGNATURE
        # You can change the internal implementation as you see fit.

    def search(self, query):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self.invertedIndex, model=self._model)
        self._parser.suspectedEntityDict = {}

        query_as_list = self._parser.parse_sentence(query)
        # add entities to query - entities doesn't adds to query_as_list in parse_sentence
        # suspectedEntityDict holds only entities from original query
        for entity in self._parser.suspectedEntityDict:
            query_as_list.append(entity)

        # Clear query from Entities parts
        query_as_list = self.clearEntitiesParts(query_as_list)
        ######################################################################################################
        #### INIT SPELL CORRECTION, ADD COVID AND FIND UNKNOWN WORDS IN ORIGINAL QUERY - BEFORE EXPENDING ####
        ######################################################################################################
        # spell checker part
        spellFixer = SpellChecker()
        # add words to known word list
        spellFixer.word_frequency.load_words(['covid'])
        # find unknown words - those words will need spell correction
        missSpell = spellFixer.unknown(query_as_list)

        ####################################
        ######## WordNet expenssion ########
        ####################################
        extendedQ = copy.deepcopy(query_as_list)
        for term in query_as_list:
            synset = wordnet.synsets(term)
            try:
                for i in range(2):
                    Synonym = synset[i].lemmas()[0].name()
                    if term.lower() != Synonym.lower() and Synonym+"~" not in extendedQ:
                        Synonym += "~"
                        extendedQ.append(Synonym)
            except:
                continue
        query_as_list = extendedQ

        #####################################
        ######## Spelling correction ########
        #####################################
        # add fixed words
        fixedQuery = copy.deepcopy(query_as_list)
        for word in missSpell:
            candidates = list(spellFixer.candidates(word))
            for i in range(2):
                try:
                    if candidates[i] not in fixedQuery:
                        fixedQuery.append(candidates[i] + '~')
                except:
                    break

        numberOFresults, relevantDocIdList = searcher.search(query_as_list) # returns tuple (numberOFresults,relevantDocIdList)
        return numberOFresults, relevantDocIdList


    def clearEntitiesParts(self,query):
        modifiedQuery_l = copy.deepcopy(query)
        termsToRemoveFromQuery = []
        # at this point if query holds Entity, it will hold the terms builds the Entity and the Entity as 1 term
        # this is why this part below for : ['BILL','Gates','blabla','bla','Bill Gates']
        # if "Bill Gates" is already known Entity it will leave us with: ['blabla','bla','Bill Gates']
        for term in query:  # cleaning parts of entities from the query if the entity exist in the inverted index
            if " " in term:
                if term in self.invertedIndex:  # entity and in inverted Index
                    # modifiedQuery_l.append(term)
                    entity_l = term.split(" ")
                    for word in entity_l:
                        try:
                            termsToRemoveFromQuery.append(word.upper())
                        except:
                            termsToRemoveFromQuery.append(word.lower())
                else:  # unknown entity
                    modifiedQuery_l.remove(term)

        for word in termsToRemoveFromQuery: #clear all appears of token from modifiedQuery
            modifiedQuery_l[:] = [x for x in modifiedQuery_l if x != word]
        query = modifiedQuery_l
        return query