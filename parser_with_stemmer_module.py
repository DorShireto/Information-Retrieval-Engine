from nltk import TweetTokenizer
from nltk.stem import SnowballStemmer
import re
from stemmer import Stemmer
from parser_module import Parse


class ParserWithStemmer(Parse):

    def parse_sentence(self, text, urls=None, tweetID=0):
        """
        This function tokenize, remove stop words for every word within the text
        :param text:
        :return:
        """

        # Pre Processes for covid rule

        fullText = re.split(' |, ', text)
        modif_text = ""
        for token in fullText:
            if token in self.preProcess_d:
                modif_text += self.preProcess_d[token] + " "
            else:
                modif_text += token + " "
        text = modif_text

        if urls != None:
            urls_dict = eval(urls)
        tweetTokenizer = TweetTokenizer()
        full_text_tokens = tweetTokenizer.tokenize(text)
        text_tokens_without_stopwords = []
        counter = 0
        while counter < len(full_text_tokens):
            token = full_text_tokens[counter]
            if self.emoji_regex.match(token):
                counter += 1
                continue
            # Checking if token builds entity
            if token[0].isupper():
                fullEntity = self.getFullEntity(counter, full_text_tokens)
                # print(fullEntity[1])
                if fullEntity[0] > 1:
                    # break the entity to token & put each token into text_tokens_without_stopwords
                    entityTokens = fullEntity[1].split(' ')
                    for token in entityTokens:
                        text_tokens_without_stopwords.append(token.upper())
                    counter += (fullEntity[0])
                    entityTerm = fullEntity[1]
                    if entityTerm not in self.docEntities:
                        self.docEntities.append(entityTerm)
                    try:
                        if entityTerm in self.suspectedEntityDict:  # entity exist
                            if tweetID in self.suspectedEntityDict[entityTerm]:  # entity exist and tweet id exist
                                (self.suspectedEntityDict[entityTerm])[tweetID][1] += 1 #TODO add [1] after [tweetid]
                            else:
                                (self.suspectedEntityDict[entityTerm])[tweetID] = [1,1] #TODO add [1] after [tweetid]
                        else:
                            self.suspectedEntityDict[entityTerm] = {tweetID: [1,1]} # tf = 1 is default because it will be overwriten later anyways...
                    except:
                        raise Exception("Error in parse with stem in entity")
                    continue
            if token.lower() not in self.stop_words and not (token.isalpha() and len(token) == 1):
                if token[0] == '#':
                    if len(token) > 1:
                        self.hastag_rule(text_tokens_without_stopwords, token)
                    else:
                        counter += 1
                        continue
                elif token[0] == '@':
                    text_tokens_without_stopwords.append(token)
                elif self.url_regex.match(token):  # URL in tweet
                    self.url_rule(text_tokens_without_stopwords, urls_dict.get(token))
                elif self.url_regex.match(token) and urls == None:  # URL in query
                    self.url_rule(text_tokens_without_stopwords, token)
                elif self.numbers_regex.match(token):
                    counter = self.number_rule(text_tokens_without_stopwords, counter, full_text_tokens, text)
                elif self.fractions_regex.match(token) and len(text_tokens_without_stopwords) > 0 and \
                        text_tokens_without_stopwords[-1].isdecimal() and text_tokens_without_stopwords[-1].count(
                    '.') == 0:
                    fraction = text_tokens_without_stopwords[-1] + ' ' + token
                    text_tokens_without_stopwords[-1] = fraction
                else:
                    try:
                        token = self.snStemmer.stem_term(token)
                    except:
                        raise Exception("Error in parse_sentence  when {} appeared",token)
                    if token[0].islower():
                        text_tokens_without_stopwords.append(token.lower())
                    else:
                        text_tokens_without_stopwords.append(token.upper())
            counter += 1
        # ext_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]
        return text_tokens_without_stopwords


    def hastag_rule(self, tokensList, hashtag):
        """
        This function implemnt the Hashtag rule and adding the new tokens to the tokensList, excluding stop-words
        :param tokensList - list of tokens
        :param hashtag - string that start with # - like #LoveBeer
        :e.g:   #LoveBeer -> #lovebeer , love, beer
        """
        hashtag2 = hashtag.replace("_", "")
        tokensList.append(hashtag2.lower())
        temp = (w for w in re.findall(r'[a-zA-Z0-9](?:[a-z0-9]+|[A-Z0-9]*(?=[A-Z]|$))', hashtag))
        for w in temp:
            try:
                w = self.snStemmer.stem_term(w)
            except:
                raise Exception("Error in hastag_rule  when {} appeared", w)
            tokensList.append(w)