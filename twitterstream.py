from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.utils import import_simplejson
json = import_simplejson()

import string
from time import sleep

class TwitterListener (StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """

    def __init__(self, nwords = 300):
        StreamListener.__init__(self)
        self.word_list = []
        self.nwords = nwords
        return

    def on_data(self, data):
        ddata = json.loads(data)
        if "text" not in ddata:
            return True

        word_list = self.word_list
        new_words = ddata["text"].split()
        # Trim out url's, unprintable characters, and @ people things
        for word in new_words:
            pop = False
            badwords = ['\\','http','@']
            if word.lower() == 'rt':
                pop = True
            for bad in badwords:
                if string.find(word,bad) > -1:
                    #print string.find(word,bad)
                    #print "found a bad word: " + word + " had: "  + bad
                    pop = True
            if pop == True:
                new_words.pop(new_words.index(word))

        # If there are too many words, trim it down
        total_len = len(word_list) + len(new_words)
        extra = total_len - self.nwords
        for x in range(extra):
            word_list.pop(0)
        # Append our new words
        for word in new_words:
            word_list.append(word)
        self.word_list = word_list

        sleep(10)
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    print "Depreciated"

