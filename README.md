twitter-cloud
=============
A program to keep you abreast of a few twitter topics. Uses pygame to draw wordclouds of words mentioned in association with the topics of your choice.

Install
=============
Install the required dependencies listed below.

When installing word_cloud, in setup.py change name="word_cloud" to name="wordcloud". (For some reason I can't get python to recognize the package any other way.)

You will need to input your own oAuth keys either into a file, or into twitterstream.py

Run twitter-cloud.py the first few lines of main allow for user specification: screen size, the keywords to track, and the maximum number of words to keep associated with each keyword.

Currently, there is no good way of exiting, so you'll have to kill the process :(

Dependencies
=============
 - pygame
 - tweepy
 - wordcloud: https://github.com/amueller/word_cloud
 - PIL
 - scikit-learn

