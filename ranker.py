# you can change whatever you want in this module, just make sure it doesn't
# break the searcher module
import utils
import math
from queue import PriorityQueue
from configuration import ConfigClass


class Ranker:
    def __init__(self):
        self.tweets_info = utils.load_obj(ConfigClass.get_output()+"/tweets_info")
        self.tweet_SigmaWij_d = {}  # key: tweetID -> value: [number of the query words showed in tweet,Sum(Wij)]

    def rank_relevant_docs(self, relevant_docs, query_as_list):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_docs: list of tuples (numOfQueryWordsInTweet,tweetID) of documents that contains at least one term from the query.
        :return: sorted list of tweetIDs by cosSim score rank
        """
        #calc Sigma(Wiq^2) of query vertor
        queryWeight = 0
        for word in query_as_list:
            if word[-1] == "~":
                queryWeight += pow(ConfigClass.expendedWordWeight,2)
            else:
                queryWeight += pow(ConfigClass.wordFromOGQueryWeight,2)


        # relevant_doc is list of tuple: (numOfApper , tweetID)
        relevant_doc_similarity_pq = PriorityQueue()
        for numAppear_tweetID_tuple in relevant_docs:
            tweetID = numAppear_tweetID_tuple[1]
            mone = self.tweet_SigmaWij_d.get(tweetID)[1]  # weight was calculated in searcher
            mehane = math.sqrt(self.tweets_info.get(tweetID)[0] * queryWeight)
            cosSim = mone / mehane
            rank = cosSim * ConfigClass.cosSinWeight + mone * ConfigClass.innerProductWeight
            relevant_doc_similarity_pq.put((-rank, tweetID))

        sortedTweetID_l = []
        while relevant_doc_similarity_pq.qsize() > 0:
            sortedTweetID_l.append(relevant_doc_similarity_pq.get()[1])

        return sortedTweetID_l

