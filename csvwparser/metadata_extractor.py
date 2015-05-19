import logging
import urllib2
import os
import json
from csvwparser import metadata

__author__ = 'sebastian'
logger = logging.getLogger(__name__)

# 1. command-line option
# 2. metadata embedded within the tabular data file itself
# 3. metadata in a document linked to using a Link header associated with the tabular data file
HEADER_LINK = ['link', 'Link']
# 4. file-specific metadata in a document located based on the location of the tabular data file
FILE_SPECIFIC_METADATA = '-metadata.json'
# 5. directory-specific metadata in a document located based on the location of the tabular data file
DIRECTORY_METADATA = 'metadata.json'


def parse_metadata(metadata_handle):
    try:
        meta_json = json.load(metadata_handle)
        meta = metadata.validate(meta_json)
        return meta
    except Exception as e:
        logger.error(e)
        raise e


def _parse_header_field(header_field):
    raise NotImplementedError()


def metadata_extraction(url, metadata_handle):
    meta_sources = []

    # case  1
    if metadata_handle is not None:
        meta_sources.append(parse_metadata(metadata_handle))

    if url:
        # case 3
        response = urllib2.urlopen(url)
        header = response.info()
        if header is not None:
            for link in HEADER_LINK:
                if link in header:
                    header_field = header[link]
                    logger.debug('found link in http header: %s', header_field)
                    meta_sources.append(_parse_header_field(header_field))

        # case 4
        retrievable = True
        try:
            meta_url = url + FILE_SPECIFIC_METADATA
            logger.debug('looking for file specific metadata: %s', meta_url)
            response = urllib2.urlopen(meta_url)
        except urllib2.URLError:
            retrievable = False
        if retrievable:
            meta_sources.append(parse_metadata(meta_url))

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
            meta_sources.append(parse_metadata(meta_url))

    return meta_sources