import math

import utils
from queue import PriorityQueue
from parser_module import Parse
from ranker import Ranker
import utils
import copy
from configuration import ConfigClass


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        # self._model = model
        self.parser = parser
        self.ranker = Ranker(indexer.tweet_info)
        self.inverted_index = indexer.inverted_idx
        self.firstUnion = True
        self.posting_dir = ConfigClass.get_output()
        # self.DocsToRetrieve = 2000
        self.DocsToRetrieve = ConfigClass.numOfDocsToRetrieve
        self.scoreLowerBoundFactor = 0.5

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - (list after extension, len of original query)
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """

        query_as_list = query
        relevant_docs, qLen = self.relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = self.ranker.rank_relevant_docs(relevant_docs,query_as_list)
        if k is not None and k>0 and k<n_relevant:
            ranked_doc_ids = ranked_doc_ids[:k]
            return k, ranked_doc_ids

        return n_relevant, ranked_doc_ids


    """
    This function  count the amount of words from query that appear in each document.
    :param query: query
    :return: list (max size of self.DocsToRetrieve ) of relevant documents (first will be document that all terms in the query
     appeared in the tweet), and len of the query
    """
    def relevant_docs_from_posting(self, query):
        #the query comes at its Expended form
        sorted_l = []
        if len(query) == 0:  # empty query
            return [], 0
        relevantDocs_pq = PriorityQueue()
        modifiedQuery_l = copy.deepcopy(query)

        termsToRemoveFromQuery = []
        # at this point if query holds Entity, it will hold the terms builds the Entity and the Entity as 1 term
        # this is why this part below for : ['BILL','Gates','blabla','bla','Bill Gates']
        # if "Bill Gates" is already known Entity it will leave us with: ['blabla','bla','Bill Gates']
        for term in query:  # cleaning parts of entities from the query if the entity exist in the inverted index
            if " " in term:
                if term in self.inverted_index:  # entity and in inverted Index
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
        #count the original query len (words without ~ at the end)
        i=0
        notExpendedQueryLen=0
        word = query[i]
        while word[-1] != '~':
            notExpendedQueryLen += 1
            i += 1
            try:
                word = query[i]
            except:
                break
        if notExpendedQueryLen >= ConfigClass.shortQueryLen: #long query
            self.scoreLowerBoundFactor = ConfigClass.longQueryFactor
        else:
            self.scoreLowerBoundFactor = ConfigClass.shortQueryFactor
        minScoreForEntry = self.scoreLowerBoundFactor * notExpendedQueryLen


        # clear query for terms that are not in Inverted Index:
        listOfValidTerms = []
        for term in query:  # term can be mix of upper and lower, or one of them. if not term doesn't exist in II
            expendedToken = False
            if term[-1] == "~":
                expendedToken = True
                term = term[:-1]
            #count the number of words in query that appear in inverted index(doesnt matter if lower or upper)
            if term.lower() in self.inverted_index:
                if expendedToken:
                    term += "~"
                term = term.lower()
            elif term.upper() in self.inverted_index:
                if expendedToken:
                    term += "~"
                term = term.upper()
            elif term in self.inverted_index:# only for entity
                if expendedToken:
                    term += "~"
            else:
                continue
            listOfValidTerms.append(term)

        ###################################################
        #######          SEARCHING PART               #####
        ###################################################

        numOfValidTerms = len(listOfValidTerms)
        if numOfValidTerms == 0:  # No vaild terms in query
            return [], 0

        if numOfValidTerms == 1:  # Only 1 word out of the query was founded in II
            term = listOfValidTerms[0]
            if term[-1] == "~": #only for expended token
                factor = ConfigClass.expendedWordWeight
                term = term[:-1]
            else:
                factor = ConfigClass.wordFromOGQueryWeight
            nodes_l = self.inverted_index[term][2]
            for node in nodes_l:
                max_f = self.ranker.tweets_info[node.tweetID][1]
                self.ranker.tweet_SigmaWij_d[node.tweetID] = [node.tf * max_f, node.Wij*factor]  # node.tf*max_f : is a rollback to num of appearance of term in tweet
                score = node.tf * max_f  # num of appear of query word in this specific tweet-node
                ##################################
                if score >= minScoreForEntry:
                    relevantDocs_pq.put((-score, node.tweetID))  # -score is to reverse the queue to max priority first.
                ##################################
                # relevantDocs_pq.put((-score, node.tweetID))  # -score is to reverse the queue to max priority first.
            while len(sorted_l) < self.DocsToRetrieve and relevantDocs_pq.qsize() > 0:
            # while relevantDocs_pq.qsize() > 0:
                itemFromPq = relevantDocs_pq.get()
                positiveScore_tweetID_Tuple = (-itemFromPq[0], itemFromPq[1])
                sorted_l.append(positiveScore_tweetID_Tuple)
            return sorted_l, len(query)

        # query len > 1
        # first time we init the tweet_SigmaWij_d with values from first list of nodes that we'll unite with others later
        factor = ConfigClass.wordFromOGQueryWeight
        term = listOfValidTerms[0]
        if term[-1] == "~": #check if first word in valid terms is an expended word
            term = term[:-1]
            factor = ConfigClass.expendedWordWeight
        unionList = self.inverted_index[term][2]  # list of nodes
        for node in unionList:
            self.ranker.tweet_SigmaWij_d[node.tweetID] = [1, node.Wij*factor]

        for i in range(1, len(listOfValidTerms)):
            term = listOfValidTerms[i]
            if term[-1] == "~":  # check if first word in valid terms is an expended word
                term = term[:-1]
                factor = ConfigClass.expendedWordWeight
            else:
                factor = ConfigClass.wordFromOGQueryWeight
            unionList = self.UnionLists(unionList, self.inverted_index[term][2],factor)

        for node in unionList:
            score = self.ranker.tweet_SigmaWij_d[node.tweetID][
                0]  # num of appear of query word in this specific tweet-node
            ##################################
            if score >= minScoreForEntry:
                relevantDocs_pq.put((-score, node.tweetID))  # -score is to reverse the queue to max priority first.
            ##################################
            # relevantDocs_pq.put((-score, node.tweetID))  # -score is to reverse the queue to max priority first.
        while len(sorted_l) < self.DocsToRetrieve and relevantDocs_pq.qsize() > 0:
        # while relevantDocs_pq.qsize() > 0:
            itemFromPq = relevantDocs_pq.get()
            # if len(sorted_l) == 0:#TODO Debug
            # print("Score: ", -itemFromPq[0], "  TweetID: ", itemFromPq[1])#TODO Debug
            positiveScore_tweetID_Tuple = (-itemFromPq[0], itemFromPq[1])
            sorted_l.append(positiveScore_tweetID_Tuple)
        return sorted_l, len(query)


    def UnionLists(self, listA, listB, factor): #factor will be 1 for term from original query, 0.5 foe expended term
        listA_len, listB_len = len(listA), len(listB)
        tweet_SigmaWij_d = self.ranker.tweet_SigmaWij_d
        a, b = 0, 0
        union_l = []
        while a < listA_len and b < listB_len:
            if listA[a] < listB[b]:
                union_l.append(listA[a])
                a += 1
            elif listB[b] < listA[a]:  # update Wij, update numOfApeers in tweet
                union_l.append(listB[b])
                if listB[b].tweetID in tweet_SigmaWij_d:
                    tweet_SigmaWij_d.get(listB[b].tweetID)[0] += 1  # numOfAppers
                    tweet_SigmaWij_d.get(listB[b].tweetID)[1] += listB[b].Wij*factor  # update Wij
                else:
                    tweet_SigmaWij_d[listB[b].tweetID] = [1, listB[b].Wij*factor]
                b += 1
            else:
                union_l.append(listB[b])
                # update Wij WITH B Wij, update numOfApeers (+1) in tweet
                tweet_SigmaWij_d.get(listB[b].tweetID)[0] += 1  # numOfAppers
                tweet_SigmaWij_d.get(listB[b].tweetID)[1] += listB[b].Wij*factor  # update Wij
                b += 1
                a += 1

        while a < listA_len:
            union_l.append(listA[a])
            a += 1

        while b < listB_len:
            union_l.append(listB[b])
            # update Wij WITH B Wij, update numOfApeers (+1) in tweet
            if listB[b].tweetID in tweet_SigmaWij_d:
                tweet_SigmaWij_d.get(listB[b].tweetID)[0] += 1  # numOfAppers
                tweet_SigmaWij_d.get(listB[b].tweetID)[1] += listB[b].Wij*factor  # update Wij
            else:
                tweet_SigmaWij_d[listB[b].tweetID] = [1, listB[b].Wij*factor]
            b += 1

        return union_l
