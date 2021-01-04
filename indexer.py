import bisect
import copy
import math
import os
import re
import utils
from posting_node import PostingNode
from configuration import ConfigClass

# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        # PostingDict - key: term value - > [ Posting nodes ]
        self.onlyDigitLettersRegex = re.compile('[A-Za-z0-9]+')
        # self.cache = {}
        self.inverted_idx = {}
        self.tweet_info = {}
        # self.posting_dir = ConfigClass.savedFileMainFolder
        self.num_of_docs_indexed = 0
        # self.docs_indexed_limit = 1000000
        self.counter = 0
        # self.counterLimit = 3
        # self.init_postings()

    # def init_postings(self):
    #     try:
    #         for i in range(self.counterLimit):
    #             name = "p" + str(i)
    #             utils.save_obj({}, self.posting_dir + "/" + name)
    #             self.cache[name] = {}
    #     except:
    #         raise Exception("Error in init_postings")

    # def write_cache_to_disk(self):
    #     """
    #     step1: loop over the cache_posting keys:
    #         step1.1 load the key's posting file
    #         step1.2:  go over all terms in value of the cache_posting key
    #                   and check if the term exist in the posting file
    #         step1.3: if term exist: append the posting nodes to the list (in the posting file)
    #         step1.4: else: add the term to the posting file with the posting node list
    #         step1.5: save posting
    #     step2: jump to step1
    #     """
    #     # print("flushing")  # TODO debug
    #     for postingFileName in self.cache:
    #         file = utils.load_obj(self.posting_dir + "/" + postingFileName)
    #         terms_in_cache = self.cache.get(postingFileName)
    #         for term in terms_in_cache:
    #             if term in file:
    #                 for node in terms_in_cache[term]:
    #                     file.get(term).append(node)
    #             else:
    #                 file[term] = terms_in_cache[term]
    #         utils.save_obj(file, self.posting_dir + "/" + postingFileName)
    #         # Clear cache
    #         self.cache[postingFileName] = {}


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via ('inverted index')
        :param document: a document need to be indexed.
        :return: -
        """
        self.num_of_docs_indexed += 1
        self.tweet_info[document.tweet_id] = [0, document.max_f, len(document.term_doc_dictionary.keys())]
        documentTerms_d = document.term_doc_dictionary
        for term in documentTerms_d:
            # if self.num_of_docs_indexed == self.docs_indexed_limit:
            #     # print("Writing catch to disk - from add new doc")  # TODO debug
            #     self.write_cache_to_disk()
            #     self.num_of_docs_indexed = 0
            try:

                # Update inverted index
                # postingName = "p" + str(self.counter)  # getting the name of the posting file for the term
                # self.counter += 1
                # if self.counter >= self.counterLimit:
                #     self.counter = 0

                if term[0].isupper() and term.lower() in self.inverted_idx:
                    term_tf = document.temrs_tf_dict[term]
                    term = term.lower()
                    # postingName = self.inverted_idx[term][2]

                elif term[0].islower() and term.upper() in self.inverted_idx:  # term is lower
                    #remove term.upper from inverted index and replace him as lower , but keep the original values.
                    termValuesFromII = copy.deepcopy(self.inverted_idx[term.upper()])
                    del self.inverted_idx[term.upper()]
                    self.inverted_idx[term]=termValuesFromII
                    term_tf = document.temrs_tf_dict[term]
                    # postingName = self.inverted_idx[term.upper()][2]
                else:#not appear. the term all UPPER either all LOWER
                    term_tf = document.temrs_tf_dict[term]

                if term not in self.inverted_idx:
                    self.inverted_idx[term] = [1, None, []]

                else:# term already in inverted index
                    self.inverted_idx[term][0] += 1  # update the df of term (df=num of documents term appear in)
                    # postingName = self.inverted_idx[term][2]
                termAppearInTweet = term_tf * document.max_f
                postingNode = PostingNode(document.tweet_id, term_tf, None, termAppearInTweet)

                #insert postingNode to the list in inverted Index:
                bisect.insort(self.inverted_idx[term][2], postingNode) #sorted insert
                # self.inverted_idx[term][2].append(postingNode)
            except:
                print('problem with the following key {}'.format(term), "docNum = ", self.num_of_docs_indexed)

    def addEntities(self, suspectedEntityDict):
        """This method will check if suspected entity have appeared
        more the once in the corpus, if so: will index and add to inverted index in order by tweetID"""
        # print("start entity adding")#TODO debug
        for entity in suspectedEntityDict:

            nodeList = []
            list_of_tweet_ID = suspectedEntityDict.get(entity).keys()
            list_of_tweet_ID_len = len(list_of_tweet_ID)
            NumOfAppearsOfEntityInCorpus = 0
            if list_of_tweet_ID_len > 1:
                # entity appears more than once so its a valid entity
                for tweetID in list_of_tweet_ID:
                    entityNumOfAppearInTweet = suspectedEntityDict.get(entity).get(tweetID)[1]
                    NumOfAppearsOfEntityInCorpus += entityNumOfAppearInTweet
                    if tweetID not in self.tweet_info:  # probs - tweet includes only entites
                        self.tweet_info[tweetID] = [0, entityNumOfAppearInTweet, 1]  #tweet doesnt exits in tweetInfo:
                                                                                    # it means that  entityNumOfApearInTweet is the max_f of that tweet
                    else:  # doc origanlly didn't count entites in term_dict
                        # dont worry , entity can not apear twice in suspectedEntityDict
                        self.tweet_info[tweetID][2] += 1
                    """
                    #updating cuz max_f ignored entity count  but we need to check who is bigger ,
                    regular word or entity appear in the same tweet
                    """
                    # self.tweet_info[tweetID][1]=max(self.tweet_info[tweetID][1],entityNumOfAppearInTweet)#comment above
                    tf = suspectedEntityDict.get(entity).get(tweetID)[0]
                    bisect.insort(nodeList,PostingNode(tweetID, tf, None, entityNumOfAppearInTweet))
                    # nodeList.append(PostingNode(tweetID, tf, None, entityNumOfAppearInTweet))

                # postingFileName = "p" + str(self.counter)  # getting the name of the posting file for the term
                # self.counter += 1
                # if self.counter >= self.counterLimit:
                #     self.counter = 0
                try:
                    self.inverted_idx[entity] = [list_of_tweet_ID_len, None, nodeList]# entity never appeared before in inverted index anyways

                except:
                    print("INDEXER.addEntities: problem with Entity: ", entity)

        # self.write_cache_to_disk()

    def update_idfWij(self, numOfDocsInCorpus):
        """
        calculates and update idf and Wij for each term in Inverted Index
        Return : nothing
        """
        for term in self.inverted_idx:
            #calc and update IDF
            df = self.inverted_idx[term][0]
            idf = math.log(numOfDocsInCorpus / df, 2)
            self.inverted_idx[term][1] = idf
            # calc Wij
            postingNodesList = self.inverted_idx[term][2]
            for node in postingNodesList:
                tf = node.tf
                if " " in term:  # Could only happen for entities
                    node.Wij = tf * idf * 2 #give double weight because Entity worth more
                else:
                    node.Wij = tf * idf #regular weight
                self.tweet_info.get(node.tweetID)[0] += math.pow(node.Wij, 2) #update Sigma(Wij^2)




        # for counter in range(self.counterLimit):
        #     fileName = "p" + str(counter)
        #     file = utils.load_obj(self.posting_dir + "/" + fileName)
        #     terms_l = list(file.keys())
        #     while len(terms_l) > 0:
        #         term = terms_l[0]
        #         if not self.onlyDigitLettersRegex.fullmatch(term):  # enter only for names
        #             terms_l.remove(term)
        #             continue
        #         if (term[0].islower() and term.upper() in file) or (term[0].isupper() and term.lower() in file):
        #             postingNodes_l = file[term.upper()]
        #             if term.lower() != term.upper():
        #                 for node in postingNodes_l:
        #                     file[term.lower()].append(node)
        #             file.pop(term.upper())
        #             self.inverted_idx.pop(term.upper())
        #             terms_l.remove(term.lower())
        #             terms_l.remove(term.upper())
        #         else:
        #             terms_l.remove(term)
        #     modifiedFile = {}
        #     for term in file:
        #         nodes_l = file.get(term)
        #         if len(nodes_l) == 1:
        #             self.inverted_idx.pop(term)
        #             continue
        #         # print("sorting ",fileName , term) #todo DEBUG
        #         nodes_l.sort()
        #         modifiedFile[term] = nodes_l
        #
        #
        #
        #         # updating Wij, idf
        #
        #
        #         for node in nodes_l:
        #
        #     utils.save_obj(modifiedFile, self.posting_dir + "/" + fileName)


    """
    From this part down, we need to implement according to partC
    """

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        try:
            return utils.load_obj(fn)
        except:
            # path = self.posting_dir
            # arr = os.listdir(path)
            raise Exception("INDEXER: file doesn't exist:", fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        try:
            utils.save_obj(self.inverted_idx, fn)
        except:
            raise Exception("INDEXER: Failed to save inverted index")



    """
    I don't think we need those method below
    """
    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term): #TODO
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.inverted_idx

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term): #TODO
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []
