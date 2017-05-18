# Use Tweepy to retrieve all the post data 


#Import the necessary methods from tweepy library

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy 
import csv
import sys 

#Variables that contains the user credentials to access Twitter API 
access_token = "860289631379697664-8zjf8xVsOerunuDiEPQtVFssIGI7ewz"
access_token_secret = "SECRET"
consumer_key = "j37pbECfjb4sy9tlDHoz9pGo1"
consumer_secret = "SECRET"


# authentification to access twitter data 
#def authetification():
#This handles Twitter authetification and the connection to Twitter Streaming API


def write_to_csv(kwd, d_from, d_to, loc, num_data):
    # open/Create a file with the filename to append data
    csvFile = open('data.csv', 'a')
    # use csv writer
    csvWriter = csv.writer(csvFile)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    for tweet in tweepy.Cursor(api.search, q= "Trump",count = 100, since="2017-05-02", until="2017-05-03", lang="en").items():
        print tweet.created_at, tweet.text
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])

def main():

    keyword = raw_input("Enter keyword for search: ")
    data_from = raw_input("Enter start date for search: ")
    data_to = raw_input("Enter end date for search: ")
    location = raw_input("Enter location (state) for search: ")
    num_data = raw_input("Enter number of tweets for search: ")
    write_to_csv(keyword, data_from, data_to, location, num_data)

    

if __name__ == '__main__':
    # calling main function 

    main() 

 








