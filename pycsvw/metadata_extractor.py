import logging
import urllib2
import os
import simplejson
from pycsvw import metadata

__author__ = 'sebastian'
logger = logging.getLogger(__name__)

# 1. command-line option
# 2. metadata embedded within the tabular data file itself
# 3. metadata in a document linked to using a Link header associated with the tabular data file
HEADER_LINK = ['link', 'Link']
# 4. file-specific metadata in a document located based on the location of the tabular data file
FILE_SPECIFIC_METADATA = '-metadata.json'
# 5. directory-specific metadata in a document located based on the location of the tabular data file
DIRECTORY_METADATA = ['metadata.json', 'csv-metadata.json']


def parse_to_json(metadata_handle):
    meta_json = simplejson.load(metadata_handle)
    # meta = metadata.validate(meta_json)
    return meta_json


def _parse_header_field(header_field):
    raise NotImplementedError()


def metadata_extraction(url, metadata_handle, embedded_metadata=False):
    meta_sources = []

    # case  1
    if metadata_handle is not None:
        meta_sources.append(parse_to_json(metadata_handle))

    # case  2
    if embedded_metadata:
        meta_sources.append(embedded_metadata)

    if url:
        # case 3
        try:
            response = urllib2.urlopen(url)
            header = response.info()
            if header is not None:
                for link in HEADER_LINK:
                    if link in header:
                        header_field = header[link]
                        logger.debug('found link in http header: %s', header_field)
                        meta_sources.append(_parse_header_field(header_field))
        except urllib2.URLError:
            pass

        # case 4
        try:
            meta_url = url + FILE_SPECIFIC_METADATA
            response = urllib2.urlopen(meta_url)
            if response.getcode() == 200:
                logger.debug('found file specific metadata: %s', meta_url)
                meta_sources.append(parse_to_json(response))
        except urllib2.URLError:
            pass

        # case 5
        for dir_meta in DIRECTORY_METADATA:
            try:
                # split away the part after the last slash
                directory = url.rsplit('/', 1)[-2]
                meta_url = os.path.join(directory, dir_meta)
                response = urllib2.urlopen(meta_url)
                if response.getcode() == 200:
                    logger.debug('found directory specific metadata: %s', meta_url)
                    meta_sources.append(parse_to_json(response))
                    break
            except urllib2.URLError:
                pass

    return meta_sources
