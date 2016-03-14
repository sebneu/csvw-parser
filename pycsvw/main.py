from StringIO import StringIO
import urllib2
import logging
import csv_parser
import metadata
import json_generator
import metadata_extractor


__author__ = 'sebastian'

logging.basicConfig()
logger = logging.getLogger(__name__)


class CSVW:
    def __init__(self, url=None, path=None, handle=None, metadata_url=None, metadata_path=None, metadata_handle=None, date_parsing=False):
        # http://www.w3.org/TR/2015/WD-tabular-data-model-20150416/#processing-tables
        if handle:
            logger.warning('"handle" is used only for testing purposes')
            name = None
        elif url:
            url_resp = urllib2.urlopen(url)
            handle = StringIO(url_resp.read())
            name = url
        elif path:
            handle = open(path, 'rb')
            name = path
        elif path and url:
            raise ValueError("only one argument of url and path allowed")
        else:
            raise ValueError("url or path argument required")

        # metadata_handle = None
        if metadata_path and metadata_url:
            raise ValueError("only one argument of metadata_url and metadata_path allowed")
        elif metadata_handle:
            logger.warning('"metadata_handle" is used only for testing purposes')
        elif metadata_url:
            meta_resp = urllib2.urlopen(metadata_url)
            metadata_handle = StringIO(meta_resp.read())
        elif metadata_path:
            metadata_handle = open(metadata_path, 'rb')

        # Retrieve the tabular data file.
        self.table, embedded_metadata = csv_parser.parse(handle, url)

        # TODO create settings using arguments or provided metadata
        sources = metadata_extractor.metadata_extraction(url, metadata_handle, embedded_metadata=embedded_metadata)
        self.metadata = metadata.merge(sources)

    def to_rdf(self):
        pass

    def to_json(self):
        # TODO group of tables?
        json_generator.minimal_mode(self.table, self.metadata.json()['tables'][0])
