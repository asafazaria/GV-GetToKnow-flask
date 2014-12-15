import os
import json
import feedparser
import urllib
from urllib2 import urlopen
import HTMLParser
import pymongo
import time


class StoriesCache(object):
    
    def __init__(self, server_host, server_port, data_base_name, collection_name, validity_threashold):
        self.validity_threashold = validity_threashold
        self.server_port = server_port
        self.data_base_name = data_base_name
        self.collection_name = collection_name
        
        if (server_port is None) or (server_host is None):
            self.server_connection = pymongo.MongoClient()
        else:
            self.server_connection = pymongo.MongoClient(server_host,server_port)
        
        self.cache_data = self.server_connection[data_base_name][collection_name]
        
    def store_stories_for_country(self, country, stories):
        current_time_stamp = time.time()
        for story in stories:
            document_to_cache = dict(story)
            document_to_cache['country'] = country
            document_to_cache['timestamp'] = current_time_stamp
            self.cache_data.insert(document_to_cache)
    
    def retrieve_stories_for_country(self, country, invalid_callback):
        
        if not self.has_valid_stories(country, self.validity_threashold):
            self.clear_stories_for_county(country)
            stories = invalid_callback(country)
            self.store_stories_for_country(country, stories)
            return stories
        
        documents = self.cache_data.find({'country':country})
        stories_list = list(documents)
        for story in stories_list:
            del  story['timestamp']       
            del  story['country']
        return stories_list
    
    def has_valid_stories(self, country, threashold):
        documents = self.cache_data.find({'country':country})
        if documents.count() == 0:
            return False
        currnet_time = time.time()
        for story in documents:
            if currnet_time - story['timestamp'] > threashold:
                return False
        return True
    
    def clear_stories_for_county(self, country):
        self.cache_data.remove({'country':country})



# figure out what dir we are in (needed to load other files when deploying to a server)
basedir = os.path.dirname(os.path.abspath(__file__))

# read in mapping of country names to paths to RSS feeds on the Global Voices server
f = open(basedir+'/globalvoices-countrypaths.json', 'r')
path_lookup = json.loads(f.read())

# initialise the mongodb cache
stories_cache = StoriesCache(None, None,'stories_cache', 'stories_collection', 50000)
    
def recent_stories_from(country):
    return stories_cache.retrieve_stories_for_country(country, recent_stories_from_generator)

def recent_stories_from_generator(country):
    '''
    Return a list of the last 3 stories for a given country
    '''
    h = HTMLParser.HTMLParser()
    raw_content = urlopen( _content_url_via_google_for( country ) ).read()
    content = json.loads( raw_content )
    stories = []
    for details in content['responseData']['feed']['entries']:
        stories.append( {
            'title': details['title'],
            'link': details['link'],
            'author': details['author'],
            'contentSnippet': h.unescape(details['contentSnippet'])
            } )
    return stories

def country_list():
    '''
    Return a list of all the countries with feeds on the Global Voices site
    '''
    return path_lookup.keys()

def _content_url_via_google_for(country):
    '''
    Return the URL to the RSS content for a country via the Google API, so we can get in JSON directly 
    (rather than in XML)
    '''
    return "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&num=5&q="+ urllib.quote( _rss_url_for(country).encode("utf-8") )

def _rss_url_for(country):
    '''
    Return the URL to the RSS feed of stories for a country
    '''
    return "http://globalvoicesonline.org" + path_lookup[country] + "feed";
