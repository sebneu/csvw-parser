from StringIO import StringIO
import urllib2
import messytables
from messytables import any_tableset, headers_guess, headers_processor, offset_processor, type_guess, types_processor
import logging
import metadata as meta


__author__ = 'sebastian'

logging.basicConfig()
logger = logging.getLogger(__name__)


def _from_url(url, date_parser=False):
    """

    :param url: The URL of the resource
    :return: A messytables table_set objects
    """
    response = urllib2.urlopen(url)
    f = StringIO(response.read())
    tables = _build_tables(f, url, date_parser)
    return tables


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
    def __init__(self, url, provided_metadata=None):
        self.table_set = _from_url(url)
        self.metadata = meta.metadata_extraction(url, provided_metadata)

    def to_rdf(self):
        pass

    def to_json(self):
        pass
