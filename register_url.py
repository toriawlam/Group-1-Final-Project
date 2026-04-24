#!/usr/bin/env python

# this script will accept a url to a downloadable plain-text source, read environment variables

# imports
from pymongo import MongoClient, errors
import sys
import os
import argparse
import logging
import datetime

mongo_url = 'mongodb+srv://Shlok72:Ds2002project@cluster0.d38r96k.mongodb.net/'
user = 'Shlok72'
pwd = 'Ds2002project'

def parse_args():
    try:
        url = sys.argv[1] # returns command line input after script is called
    except IndexError:
        logging.error(f"Usage: python {sys.argv[0]} <url>")
        sys.exit(1)
    return url

def check_url(this_url):
    client = MongoClient(mongo_url, username=user, password=pwd,connectTimeoutMS=200,retryWrites=True)
    db = client.text_library
    # check to see if url exists in database collection
    if db.texts.find_one({'url':this_url}):
        print("This URL already exists in the text library!")
    else:
        db.texts.insert_one({'url': this_url,
                            'status': 'unprocessed',
                            'added_at': datetime.datetime.now().isoformat()})
        print("This URL has been added to the text library!")
    
    client.close()

def main():
    this_url = parse_args()
    check_url(this_url)

if __name__ == "__main__":
    main()

    


