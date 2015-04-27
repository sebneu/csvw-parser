import json
import logging
import urllib2
import os
from StringIO import StringIO

__author__ = 'sebastian'
logger = logging.getLogger(__name__)

# 1. command-line option
# 2. metadata embedded within the tabular data file itself HOW???
# 3. metadata in a document linked to using a Link header associated with the tabular data file
# 4. file-specific metadata in a document located based on the location of the tabular data file
FILE_SPECIFIC_METADATA = '-metadata.json'
# 5. directory-specific metadata in a document located based on the location of the tabular data file
DIRECTORY_METADATA = 'metadata.json'


class Metadata(object):
    def __init__(self, dict_string):
        self.__dict__ = dict_string


def parse_metadata(meta_json):
    try:
        meta = Metadata(dict_string=meta_json)
        return meta
    except Exception as e:
        print e
        raise e

def _parse_header_field(header_field):
    raise NotImplementedError()


def metadata_extraction(url, metadata_raw):
    # case  1 or 2
    if metadata_raw is not None:
        meta_json = json.load(metadata_raw)
        return parse_metadata(meta_json)

    # case 3
    response = urllib2.urlopen(url)
    header = response.info()
    if header is not None:
        header_field = None
        if 'Link' in header:
            header_field = header['Link']
        elif 'link' in header:
            header_field = header['link']
        if header_field:
            logger.debug('found link in http header: %s', header_field)
            _parse_header_field(header_field)

    # case 4
    retrievable = True
    try:
        meta_url = url + FILE_SPECIFIC_METADATA
        logger.debug('looking for file specific metadata: %s', meta_url)
        response = urllib2.urlopen(meta_url)
    except urllib2.URLError:
        retrievable = False
    if retrievable:
        f = StringIO(response.read())
        meta_json = json.load(f)
        return parse_metadata(meta_json)

    # case 5
    retrievable = True
    try:
        # split away the part after the last slash
        directory = url.rsplit('/', 1)[-2]
        meta_url = os.path.join(directory, DIRECTORY_METADATA)
        logger.debug('looking for directory specific metadata: %s', meta_url)
        response = urllib2.urlopen(meta_url)
    except urllib2.URLError:
        retrievable = False
    if retrievable:
        f = StringIO(response.read())
        meta_json = json.load(f)
        return parse_metadata(meta_json)
