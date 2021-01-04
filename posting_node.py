class PostingNode:
    def __init__(self,tweetID,tf,Wij,numOfApearInTweet):
        self.tweetID = tweetID
        self.tf = tf
        self.Wij = Wij
        self.numOfApearInTweet=numOfApearInTweet

    def getTweetID(self):
        return self.tweetID

    def __lt__(self, other):
        return self.tweetID < other.tweetID

    def __gt__(self, other):
        return self.tweetID > other.tweetID

    def __eq__(self, other):
        return self.tweetID == other.tweetID

    def __hash__(self):
        return hash((self.tweetID))