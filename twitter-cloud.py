# Pull text from twitter containing certain keywords.
# Make a word cloud from these and display them in an artistic manner

from tweepy import OAuthHandler
from tweepy import Stream

import numpy as np
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

def stream_init(trackwords, words_max):
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    ntrack = len(trackwords)
    print "starting streams...  ",
    llist = [0]*ntrack
    slist = [0]*ntrack
    for ii in range(ntrack):
        llist[ii] = ts.TwitterListener(words_max)
        slist[ii] = Stream(auth, llist[ii])
        slist[ii].filter(track=[trackwords[ii]],async=True)
    print "done starting streams"
    return (ntrack, llist, slist)

def stream_close(slist):
    print "cleaning up streams...  ",
    for stream in slist:
        stream.disconnect()
    print "disconnected from streams."
    return

if __name__ == '__main__':
    # Initalize pygame
    pygame.init()
    fpsClock = pygame.time.Clock()
    # Start our screen surface
    screen_size = (1300,700)
    window = pygame.display.set_mode(screen_size)
    window.fill((0, 0, 0))
    pygame.display.set_caption('Twitter-Cloud v0.1')
    # Get screen size parameters for progressbars
    sw = window.get_width()
    sh = window.get_height()

    # Set user parameters
    try:
        wf = open('words.txt','r')
        trackwords = []
        for line in wf:
            trackwords.append(line.strip('\n'))
    except:
        trackwords = ['baseball','obama','nytimes']

    # Delay and list properties
    delaytime = 10000
    words_max = 200
    fullscrn = False
    # Start the streams for these words
    ntrack, llist, slist = stream_init(trackwords, words_max)
    # A wordcloud with our trackwords while we wait
    wordcloud.make_wordcloud_rawtext(\
        ''.join((word+' ')*3 for word in trackwords), 'base', sw, sh/2)
    # Enable full screen if we want it
    if fullscrn:
        pygame.display.toggle_fullscreen()

    # Scale the font for the progress bars to be 1/4th the bar height
    fh = sh/4/ntrack
    font = pygame.font.Font(None,fh)
    
    old_surface = surface_progress(window,llist,trackwords,sw,sh)
    word_ii = 0
    # Set an initial time so it refreshes the screen right away
    lasttime = pygame.time.get_ticks() - delaytime
    while True:
        # exit the loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stream_close(slist)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stream_close(slist)
                    pygame.quit()
                    sys.exit()

        # Reset our counter if it's too large
        if word_ii >= ntrack:
            word_ii = 0

        # Update the screen
        cwords = llist[word_ii].word_list
        nwords = len(cwords)
        if (pygame.time.get_ticks() - lasttime) > delaytime:
            if nwords < words_max:
                # See if there is an existing image and display that while we wait
                if os.path.exists(trackwords[word_ii]+'.bmp'):
                    new_surface = surface_cloud(window,trackwords[word_ii],sw,sh)
                    fade_AtoB(window,old_surface,new_surface)
                    old_surface = new_surface
                else:
                    new_surface = surface_progress(window,llist,trackwords,sw,sh)
                    fade_AtoB(window,old_surface,new_surface)
                    old_surface = new_surface
            else:
                make_wordcloud_rawtext(\
                    ''.join((word + ' ')*2 for word in cwords),\
                     trackwords[word_ii], sw, sh)
                new_surface = surface_cloud(window,trackwords[word_ii],sw,sh)
                fade_AtoB(window,old_surface,new_surface)
                old_surface = new_surface
            lasttime = pygame.time.get_ticks()

        # Update our word
        word_ii += 1

        # do any screen updates if needed
        pygame.display.update()
        fpsClock.tick(30)
