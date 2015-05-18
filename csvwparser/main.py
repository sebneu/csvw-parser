from StringIO import StringIO
import urllib2
import messytables
from messytables import any_tableset, headers_guess, headers_processor, offset_processor, type_guess, types_processor
import logging
import metadata_extractor as meta


__author__ = 'sebastian'

logging.basicConfig()
logger = logging.getLogger(__name__)


def _build_tables(handle, url, date_parser):
    table_set = any_tableset(handle)

    # Build meta data objects
    for row_set in table_set.tables:
        # A table set is a collection of tables:
        # guess header names and the offset of the header:
        offset, headers = headers_guess(row_set.sample)
        logger.debug('headers: %s', headers)

        row_set.register_processor(headers_processor(headers))

        # add one to begin with content, not the header:
        row_set.register_processor(offset_processor(offset + 1))

        # guess column types:
        messytables.types.BoolType.true_values = ['true', 'True', 'TRUE']
        messytables.types.BoolType.false_values = ['false', 'False', 'FALSE']
        selected_types = [messytables.types.StringType,
                          messytables.types.DecimalType,
                          messytables.types.IntegerType,
                          messytables.types.BoolType]
        if date_parser:
            selected_types.append(messytables.types.DateUtilType)

        types = type_guess(row_set.sample, types=selected_types
                           #strict=True
                           )
        logger.debug('types: %s', types)

        # and tell the row set to apply these types to
        # each row when traversing the iterator:
        row_set.register_processor(types_processor(types))

    return table_set


class CSVW:
    def __init__(self, url=None, path=None, metadata_url=None, metadata_path=None, date_parsing=False):
        if url:
            response = urllib2.urlopen(url)
            handle = StringIO(response.read())
            name = url
        elif path:
            handle = open(path, 'rb')
            name = path
        elif path and url:
            raise ValueError("only one argument of url and path allowed")
        else:
            raise ValueError("url or path argument required")

        if metadata_url:
            response = urllib2.urlopen(metadata_url)
            metadata_handle = StringIO(response.read())
        elif metadata_path:
            metadata_handle = open(metadata_path, 'rb')
        elif metadata_path and metadata_url:
            raise ValueError("only one argument of metadata_url and metadata_path allowed")
        else:
            self.metadata_handle = None

        self.table_set = _build_tables(handle, name, date_parsing)
        self.metadata = meta.metadata_extraction(url, metadata_handle)

    def to_rdf(self):
        pass

    def to_json(self):
        pass
