# Pull text from twitter containing certain keywords.
# Make a word cloud from these and display them in an artistic manner

from tweepy import OAuthHandler
from tweepy import Stream

import twitterstream as ts
import wordcloud

import pygame
import os.path
import sys

# Import our twitterkeys
f = open('twitterkeys','r')
consumer_key =  f.readline().strip('\n')
consumer_secret = f.readline().strip('\n')
access_token = f.readline().strip('\n')
access_token_secret = f.readline().strip('\n')

def make_wordcloud_rawtext(text, savename, width=400, height=200):
    import os
    import sys
    from sklearn.feature_extraction.text import CountVectorizer

    sources = [savename]

    cv = CountVectorizer(min_df=1, charset_error="ignore",
                         stop_words="english", max_features=200)
    counts = cv.fit_transform([text]).toarray().ravel()
    words = np.array(cv.get_feature_names())
    # throw away some words, normalize
    words = words[counts > 1]
    counts = counts[counts > 1]
    output_filename = (os.path.splitext(os.path.basename(sources[0]))[0]
                       + ".bmp")
    counts = wordcloud.make_wordcloud(words, counts, output_filename, width=width, height=height)

def fade_AtoB(ws,sA,sB):
    for level in range(0,256,15):
        #print "fading... " + repr(level)
        sB.set_alpha(level)
        ws.fill((0,0,0))
        ws.blit(sA, (0,0))
        ws.blit(sB, (0,0))
        pygame.display.update()
        pygame.time.wait(50)
    return

def surface_cloud(ws,cloudname,sw,sh):
    screen = pygame.Surface((sw,sh))
    fname = cloudname+'.bmp'
    cloud = pygame.image.load(fname).convert()
    screen.blit(cloud, (0, 0))
    return screen

def surface_progress(ws,llist,trackwords,sw,sh):
    screen = pygame.Surface((sw,sh))
    screen.fill((0, 0, 0))
    splash = pygame.image.load('base.bmp').convert()
    bh = sh/2/ntrack    # how high to make the progress bars
    screen.blit(splash, (0, sh/2))
    for ii in range(ntrack):
        cwords = llist[ii].word_list
        nwords = len(cwords)
        #print trackwords[ii] + repr(nwords)
        progress = ((nwords*1.0)/(words_max*1.0))*sw
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect((0,bh*ii), (progress,bh)))
        text_surface = font.render(trackwords[ii], True, (127, 127, 127))
        screen.blit(text_surface, (40,bh*ii))
    return screen

if __name__ == '__main__':
    # Set user parameters
    screen_size = (1300,700)
    trackwords = ['baseball','obama','nytimes']
    ntrack = len(trackwords)
    words_max = 500

    pygame.init()
    window = pygame.display.set_mode(screen_size)
    window.fill((0, 0, 0))
    pygame.display.update()
    pygame.display.set_caption('Twitter-Cloud v0.1')
    sw = window.get_width()
    sh = window.get_height()
    fh = sh/4/ntrack    # how high to make the progress bars
    font = pygame.font.Font(None,fh)
    
    # A wordcloud with our trackwords while we wait
    wordcloud.make_wordcloud_rawtext(\
        ''.join((word+' ')*3 for word in trackwords), 'base', sw, sh/2)

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print "starting streams..."
    llist = [0]*ntrack
    slist = [0]*ntrack
    for ii in range(ntrack):
        llist[ii] = ts.TwitterListener(words_max)
        slist[ii] = Stream(auth, llist[ii])
        slist[ii].filter(track=[trackwords[ii]],async=True)
    print "done starting streams"

    fade = False
    old_surface = surface_progress(window,llist,trackwords,sw,sh)
    mainloop = True
    while mainloop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO: clean up the exit
                pygame.quit()
                sys.exit()
                mainloop = False

        for ii in range(ntrack):
            cwords = llist[ii].word_list
            nwords = len(cwords)
            if nwords < words_max:
                new_surface = surface_progress(window,llist,trackwords,sw,sh)
                fade_AtoB(window,old_surface,new_surface)
                old_surface = new_surface
                pygame.time.wait(10000)
                # See if there is an existing image and display that while we wait
                if os.path.exists(trackwords[ii]+'.bmp'):
                    new_surface = surface_cloud(window,trackwords[ii],sw,sh)
                    fade_AtoB(window,old_surface,new_surface)
                    old_surface = new_surface
                    pygame.time.wait(10000)
                fade = False
            else:
                make_wordcloud_rawtext(\
                    ''.join((word + ' ')*2 for word in cwords),\
                     trackwords[ii], sw, sh)
                new_surface = surface_cloud(window,trackwords[ii],sw,sh)
                fade_AtoB(window,old_surface,new_surface)
                old_surface = new_surface
                pygame.time.wait(10000)
                fade = False

    print "cleaning up streams..."
    # Clean up our streams
    for stream in slist:
        stream.disconnect()
    print "disconnected from streams."

    # and quit pygame
    pygame.quit()

