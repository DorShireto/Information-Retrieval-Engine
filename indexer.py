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
        self.onlyDigitLettersRegex = re.compile('[A-Za-z0-9]+')
        self.inverted_idx = {}
        self.tweet_info = {}
        self.num_of_docs_indexed = 0
        self.counter = 0

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
            try:

                if term[0].isupper() and term.lower() in self.inverted_idx:
                    term_tf = document.temrs_tf_dict[term]
                    term = term.lower()
                elif term[0].islower() and term.upper() in self.inverted_idx:  # term is lower
                    #remove term.upper from inverted index and replace him as lower , but keep the original values.
                    termValuesFromII = copy.deepcopy(self.inverted_idx[term.upper()])
                    del self.inverted_idx[term.upper()]
                    self.inverted_idx[term]=termValuesFromII
                    term_tf = document.temrs_tf_dict[term]
                else:#not appear. the term all UPPER either all LOWER
                    term_tf = document.temrs_tf_dict[term]

                if term not in self.inverted_idx:
                    self.inverted_idx[term] = [1, None, []]

                else:# term already in inverted index
                    self.inverted_idx[term][0] += 1  # update the df of term (df=num of documents term appear in)
                termAppearInTweet = term_tf * document.max_f
                postingNode = PostingNode(document.tweet_id, term_tf, None, termAppearInTweet)

                #insert postingNode to the list in inverted Index:
                bisect.insort(self.inverted_idx[term][2], postingNode) #sorted insert
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
                    tf = suspectedEntityDict.get(entity).get(tweetID)[0]
                    bisect.insort(nodeList,PostingNode(tweetID, tf, None, entityNumOfAppearInTweet))

                try:
                    self.inverted_idx[entity] = [list_of_tweet_ID_len, None, nodeList]# entity never appeared before in inverted index anyways

                except:
                    print("INDEXER.addEntities: problem with Entity: ", entity)

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
        if fn[-4:] == ".pkl":
            fn = fn.replace(".pkl","")
        try:
            return utils.load_obj(fn)
        except:
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

    def clearInvertedIndex(self, limit):

        keysFromInvertedIndex = list(self.inverted_idx.keys())

        for key in keysFromInvertedIndex:
            if len(self.inverted_idx[key][2]) <= limit:
                self.inverted_idx.pop(key)




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
