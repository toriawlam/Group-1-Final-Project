#!/usr/bin/env python

# this script will accept a url to a downloadable plain-text source, read environment variables

# imports
from pymongo import MongoClient, errors
import os
import argparse
import logging

def parse_args():
    try:
        url = sys.argv[1] # returns command line input after script is called
    except IndexError:
        logging.error(f"Usage: python {sys.argv[0] <url>}")
        sys.exit(1)
    return url




