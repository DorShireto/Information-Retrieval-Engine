from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from document import Document
from stemmer import Stemmer
import re
from nltk.corpus import wordnet



class Parse:

    def __init__(self):
        #######################
        #self.stop_words = frozenset(stopwords.words('english')) #this line came with partC skeleton
        #######################
        stopwords_list = stopwords.words('english') + [',', '"', '...', '.', '~', '!', '?', ':', '&', '+', "'", "...",
                                                       '…', '“', '”', '..', '*', '|', ';', '(', ')', ':/', "it's",
                                                       "they'll", "they've", '. . .', "i'm", "that's", "we're", "rt",
                                                       '<3', '{', '}', 'im', "he's", '8/', "i've", '', '—', '‘', '’',
                                                       '/', '-', '♥', '❤', '️', '->', '―', '=', '3⃣9⃣7⃣', '♂', '\u200d',
                                                       '♀', '‼', '–', '▶', '•', '[', ']', '▪', '▪', ':)', ';)', '✝',
                                                       '<', '>',
                                                       '::', '\u2066', '\u2069', '⚠', ';d', '...\n\n...', '_', '☔',
                                                       '1⃣', '✅']

        self.stop_words = {stopwords_list[i]: stopwords_list[i] for i in range(len(stopwords_list))}
        self.suspectedEntityDict = {}
        self.url_regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.numbers_regex = re.compile('^([-+] ?)?[0-9]+(,[0-9]+)*?(\.[0-9]+)?$')
        self.fractions_regex = re.compile('[1-9][0-9]*\/[1-9][0-9]*')
        self.onlyDigit_Letters_Tag_HashTag_Regex = re.compile('[@#.A-Za-z0-9]+')
        self.emoji_regex = re.compile("["
                                      u"\U0001F600-\U0001F64F"  # emoticons
                                      u"\U00010000-\U0010ffff"  # emojies
                                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                      u"\U0001F1E6-\U0001F1FF"  # flags (other)                                      
                                      u"\U0001F30D-\U0001F567"  # Other additional symbols 
                                      u"\U0001F468-\U0001F9F1"  # Family 
                                      u"\U0001F3fB-\U0001F9DF"  # Gendered 
                                      u"\U0001F468-\U0001F9D1"  # Hair 
                                      u"\U0001F191-\U0001F6F3"  # More others options
                                      u"\U0001F3FB-\U0001F9DD"  # RGI_Emoji_Modifier_Sequence                                
                                      "]", flags=re.UNICODE)

        self.docEntities = []
        self.snStemmer = Stemmer()
        self.preProcess_d = {"covid": "covid", "COVID": "covid", "covid-19": "covid", "COVID-19": "covid",
                             "Covid-19": "covid", "covid19": "covid", "covid_19": "covid", "covidー19": "covid",
                             "coronavirus": "covid", "sars-cov-2": "covid", "Sars-CoV-2": "covid",
                             "Sars-Cov-2": "covid", "SARS-COV-2": "covid", "SarsCoV2": "covid",
                             "Capt.": "Captain", "Capt": "Captain", "Cmdr": "Commander", "Cmdr.": "Commander",
                             "Col.": "Colonel", "Col": "Colonel", "Dr": "Doctor", "Dr.": "Doctor",
                             "Gen": "General", "Gen.": "General", "Gov": "Governor", "Gov.": "Governor",
                             "Hon": "Honorable", "Hon.": "Honorable", "Maj": "Major", "Maj.": "Major",
                             "Mr": "Mister", "Mr.": "Mister", "Mrs": "Misses", "Mrs.": "Misses", "Ms": "Miss",
                             "Ms.": "Miss", "Prof": "Professor", "Prof.": "Professor"}

    def parse_sentence(self, text, urls=None, tweetID=0):
        """
               This function tokenize, remove stop words for every word within the text
               :param text:
               :return:
               """

        # TODO: here we'll add more cleaning options to the tokenizer
        # text_tokens = word_tokenize(text)
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
                    if entityTerm in self.suspectedEntityDict:  # entity exist
                        if tweetID in self.suspectedEntityDict[entityTerm]:  # entity exist and tweet id exist
                            (self.suspectedEntityDict[entityTerm])[tweetID][1] += 1
                        else:
                            (self.suspectedEntityDict[entityTerm])[tweetID] = [1, 1]
                    else:
                        self.suspectedEntityDict[entityTerm] = {
                            tweetID: [1, 1]}  # tf = 1 is default because it will be overwriten later anyways...
                    continue
            if token.lower() not in self.stop_words and not (token.isalpha() and len(token) == 1):
                if token[0] == '#' and len(token) > 1:
                    self.hastag_rule(text_tokens_without_stopwords, token)
                elif token[0] == '@':
                    text_tokens_without_stopwords.append(token)
                elif self.url_regex.match(token):  # URL in tweet
                    if urls is None:  # if true means that url came from query as token
                        urls_dict = {token: token}
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
                    if token[0].islower():
                        text_tokens_without_stopwords.append(token.lower())
                    else:
                        text_tokens_without_stopwords.append(token.upper())
            counter += 1
        # ext_tokens_without_stopwords = [w for w in text_tokens if w not in self.stop_words]
        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = int(doc_as_list[0])
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        urls = doc_as_list[3]
        urls = urls.replace("null", "None")
        # if tweet_id == '1288852665171095557':
        #      print('ghost')

        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        quote_indices = doc_as_list[10]
        retweet_quote_text = doc_as_list[11]
        retweet_quote_urls = doc_as_list[12]
        retweet_quote_indices = doc_as_list[13]
        # 11593
        # checking if tweet inculding urls - if so swap short url with full url
        term_tf_dict = {}  # key: term, value: calculated tf
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text, urls, tweet_id)

        doc_length = len(tokenized_text)  # after text operations.

        max_f = 1  # max appearances of term in current tweet
        for term in tokenized_text:
            if term[0] == '#' or term[0] == '@':
                try:  # asumming that upper is already in dict already
                    term_dict[term] += 1
                except:
                    term_dict[term] = 1
                continue
            if term[0].islower():
                if term.upper() in term_dict:
                    try:  # asumming that lower is already in dict already
                        term_dict[term.lower()] += term_dict[term.upper()] + 1
                    except:
                        term_dict[term.lower()] = term_dict[term.upper()] + 1
                    term_dict.pop(term.upper())
                try:
                    term_dict[term.lower()] += 1
                except:
                    term_dict[term.lower()] = 1
            else:
                if term.lower() in term_dict:
                    term_dict[term.lower()] += 1
                else:
                    try:  # asumming that upper is already in dict already
                        term_dict[term.upper()] += 1
                    except:
                        term_dict[term.upper()] = 1

        try:
            max_f = max(term_dict.values())
        except:
            max_f = 1
        # tf calc
        for term in term_dict:
            term_tf_dict[term] = (term_dict[term] / max_f)

        document = Document(tweet_id, term_tf_dict, max_f, term_dict, tweet_date, full_text, urls, retweet_text,
                            retweet_url, quote_text, quote_url, doc_length)

        # calc tf values for entities
        for entity in self.docEntities:
            numOfAppear = self.suspectedEntityDict.get(entity).get(tweet_id)[1]
            entityTF = float(numOfAppear) / max_f
            self.suspectedEntityDict[entity][tweet_id][0] = entityTF


        self.docEntities = []
        return document

    """
    ************************THIS IS THE RULES FUNCTIONS PART:*************************
    ************************THIS IS THE RULES FUNCTIONS PART:*************************
    ************************THIS IS THE RULES FUNCTIONS PART:*************************
    """

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
            if w in self.preProcess_d:
                w = self.preProcess_d[w]
            tokensList.append(w.lower())

    def url_rule(self, text_tokens_without_stopwords, token):
        if token is None:
            return
        token = token.replace("https://www.", "")
        token = token.replace("https://", "")

        token = token.replace("http://www.", "")
        token = token.replace("http://", "")

        url = re.split(r'[/:?= ]', token)
        url = list(filter(None, url))  # delete white spaces from list
        text_tokens_without_stopwords.append(url[0])
        try:
            text_tokens_without_stopwords.append(url[
                                                     1])  # the only important data placed in 0 or maybe sometimes in 1st the other part of url is usually jibrish and crap
        except:
            return

    def getFullEntity(self, counter, full_text_tokens):
        """
        params: counter - index of suspected term in full_text_tokens
        params: full_text_token - list of tokens out of full_text
        function will loop over the full_text_tokens and build an entity string
        **** special rule: Entity can't be longer then 4 words ****
        return: tuple -> (number of tokens that creates the entity, full entity)
        """
        word_in_entity = 1
        entity = full_text_tokens[counter]
        if entity.isupper():
            return (word_in_entity, entity)
        while counter + 1 < len(full_text_tokens) and full_text_tokens[counter + 1][0].isupper() and full_text_tokens[
                                                                                                         counter + 1][
                                                                                                     1:].islower() and word_in_entity <= 4:
            # while counter + 1 < len(full_text_tokens) and full_text_tokens[counter + 1][0].isupper():
            entity = entity + " " + full_text_tokens[counter + 1]
            word_in_entity += 1
            counter += 1
        return (word_in_entity, entity)

    def number_rule(self, text_tokens_without_stopwords, counter, full_text_tokens, text):
        """
        params: text_tokens_without_stopwords - list of tokens that will be added to the indexer
        params: counter - location of the number in full_text_tokens
        params: full_text_tokens: list of tokens that will be checked for additional parts of the number
        function: this method will get the location of the number in full_text_tokens and will return the parsed number
        exp: 10,000 -> 10K
        exp: 10000 -> 10K
        exp: 10 thousand -> 10K
        exp: 10 -> 10
        exp 1045.56 -> 1.04K
        return: number of tokens need to skip
        """
        numbers_regex = re.compile('^([-+] ?)?[0-9]+(,[0-9]+)*?(\.[0-9]+)?$')
        sym_container = {'%': '%', 'percent': '%', 'percentage': '%', 'percents': '%', 'percentages': '%',
                         'thousands': 'K', 'thousand': 'K', 'million': 'M', 'millions': 'M', 'billion': 'B',
                         'billions': "B", '$': '$', 'dollar': '$', 'dollars': '$'}

        token = full_text_tokens[counter].replace(",", "")

        if (counter + 1) < len(full_text_tokens) and full_text_tokens[counter + 1].lower() in sym_container:
            text_tokens_without_stopwords.append(token + sym_container[(full_text_tokens[counter + 1]).lower()])
            return counter + 1

        fixed_number = self.build_number(counter, full_text_tokens, text)
        counter += fixed_number[0]

        # IP RULE
        if fixed_number[1].count('.') >= 2:
            text_tokens_without_stopwords.append(fixed_number[1])
            return counter

        if counter - 1 >= 0 and full_text_tokens[counter - 1] == '$' and text_tokens_without_stopwords[-1] == '$':
            text_tokens_without_stopwords.remove('$')
            text_tokens_without_stopwords.append(str(fixed_number[1]) + '$')
            return counter

        # At this post token should be a clean number without ","
        token = fixed_number[1]
        if float(token) < 999:
            try:  # if there's no token in counter + 1, handle the exception
                if full_text_tokens[counter + 1] in ['K', 'k', 'M', 'm', 'B', 'b']:
                    token = token + full_text_tokens[counter + 1].upper()
            except:
                pass
            text_tokens_without_stopwords.append(token)
            return counter

        number_to_divide = float(token)
        number_to_divide = number_to_divide / 1000
        cnt = 0

        while number_to_divide >= 1 and cnt < 3:
            cnt += 1
            number_to_divide = number_to_divide / 1000

        divid = [(1000, 'K'), (1000000, 'M'), (1000000000, 'B')]
        num_to_add = round(float(token) / divid[cnt - 1][0], 3)
        num_at_int = int(float(token) / divid[cnt - 1][0])
        if num_at_int == num_to_add:
            num_to_add = num_at_int
        num_to_add = str(num_to_add) + divid[cnt - 1][1]
        text_tokens_without_stopwords.append(num_to_add)

        return counter

    def build_number(self, counter, full_text_tokens, text):
        sec_number_regex = re.compile('^[0-9]+(,[0-9]+)*?(\.[0-9]+)?$')
        token = full_text_tokens[counter]
        steps = 0
        index = text.find(token)
        index += len(token)

        if index + 1 <= len(text) and text[index] == ' ' or text[index:index + 2] == ", " or text[
                                                                                             index:index + 2] == ". ":
            token = token.replace(",", "")
            return (steps, token)

        while len(full_text_tokens[counter]) == 8 and counter + 1 < len(full_text_tokens) and sec_number_regex.match(
                full_text_tokens[counter + 1]):
            token = full_text_tokens[counter] + full_text_tokens[counter + 1]
            counter += 1
            steps += 1

        while counter + 2 < len(full_text_tokens) and full_text_tokens[counter + 1] == '.' and sec_number_regex.match(
                full_text_tokens[counter + 2]):
            token = full_text_tokens[counter] + '.' + full_text_tokens[counter + 2]
            counter += 2
            steps += 2

        while counter + 1 < len(full_text_tokens) and sec_number_regex.match(full_text_tokens[counter + 1]):
            token = token + full_text_tokens[counter + 1]
            steps += 1
            counter += 1

        while (counter + 2) < len(full_text_tokens) and full_text_tokens[counter + 1] == ',' and \
                sec_number_regex.match(full_text_tokens[counter + 2]):
            if '.' in full_text_tokens[counter + 2] and '.' in token:
                return (steps, token)
            tmp = full_text_tokens[counter + 2]
            token = token + tmp
            counter += 2
            steps += 2

        token = token.replace(",", "")
        return (steps, token)
