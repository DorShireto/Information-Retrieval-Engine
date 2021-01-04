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

    def rank_relevant_docs(self, relevant_docs, qLen):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_docs: list of tuples (numOfQueryWordsInTweet,tweetID) of documents that contains at least one term from the query.
        :return: sorted list of tweetIDs by cosSim score rank
        """
        # relevant_doc is list of tuple: (numOfApper , tweetID)
        queryWordWeight = 100
        relevant_doc_similarity_pq = PriorityQueue()
        for numApper_tweetID_tuple in relevant_docs:
            tweetID = numApper_tweetID_tuple[1]
            mone = self.tweet_SigmaWij_d.get(tweetID)[1] * queryWordWeight
            # mone = self.tweets_info.get(tweetID)[3] * queryWordWeight

            mehane = math.sqrt(self.tweets_info.get(tweetID)[0] * (qLen * pow(queryWordWeight, 2)))
            cosSim = mone / mehane
            rank = cosSim * 0.7 + mone * 0.3
            relevant_doc_similarity_pq.put((-rank, tweetID))

        sortedTweetID_l = []
        while relevant_doc_similarity_pq.qsize() > 0:
            sortedTweetID_l.append(relevant_doc_similarity_pq.get()[1])

        return sortedTweetID_l

    # def retrieve_top_k(self, sorted_relevant_doc, k=1):
    #     """
    #     return a list of top K tweets based on their ranking from highest to lowest
    #     :param sorted_relevant_doc: list of all candidates docs.
    #     :param k: Number of top document to return
    #     :return: list of relevant document
    #     """
    #     if len(sorted_relevant_doc) == 0:
    #         return []
    #     finalList = []  # list of tuples (rankScore, tweetID)
    #     i = 0
    #     while i < k and i <= 2000 and i < len(sorted_relevant_doc):
    #         tweetID = sorted_relevant_doc[i]
    #         rankScore = self.tweet_SigmaWij_d.get(tweetID)
    #         finalList.append((rankScore, tweetID))
    #         i += 1
    #
    #     return finalList

