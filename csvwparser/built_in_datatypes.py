__author__ = 'sebastian'

from rdflib.namespace import XSD
from rdflib.namespace import RDF
from rdflib import Namespace

CSVW = Namespace("http://www.w3.org/ns/csvw#")


# Valid datatypes
DATATYPES = {
  'anyAtomicType':      XSD.anyAtomicType,
  'anyURI':             XSD.anyURI,
  'base64Binary':       XSD.basee65Binary,
  'boolean':            XSD.boolean,
  'byte':               XSD.byte,
  'date':               XSD.date,
  'dateTime':           XSD.dateTime,
  'dayTimeDuration':    XSD.dayTimeDuration,
  'dateTimeStamp':      XSD.dateTimeStamp,
  'decimal':            XSD.decimal,
  'double':             XSD.double,
  'duration':           XSD.duration,
  'float':              XSD.float,
  'ENTITY':             XSD.ENTITY,
  'gDay':               XSD.gDay,
  'gMonth':             XSD.gMonth,
  'gMonthDay':          XSD.gMonthDay,
  'gYear':              XSD.gYear,
  'gYearMonth':         XSD.gYearMonth,
  'hexBinary':          XSD.hexBinary,
  'int':                XSD.int,
  'integer':            XSD.integer,
  'language':           XSD.language,
  'long':               XSD.long,
  'Name':               XSD.Name,
  'NCName':             XSD.NCName,
  'negativeInteger':    XSD.negativeInteger,
  'NMTOKEN':            XSD.NMTOKEN,
  'nonNegativeInteger': XSD.nonNegativeInteger,
  'nonPositiveInteger': XSD.nonPositiveInteger,
  'normalizedString':   XSD.normalizedString,
  'NOTATION':           XSD.NOTATION,
  'positiveInteger':    XSD.positiveInteger,
  'QName':              XSD.Qname,
  'short':              XSD.short,
  'string':             XSD.string,
  'time':               XSD.time,
  'token':              XSD.token,
  'unsignedByte':       XSD.unsignedByte,
  'unsignedInt':        XSD.unsignedInt,
  'unsignedLong':       XSD.unsignedLong,
  'unsignedShort':      XSD.unsignedShort,
  'yearMonthDuration':  XSD.yearMonthDuration,

  'any':                XSD.anyAtomicType,
  'binary':             XSD.base64Binary,
  'datetime':           XSD.dateTime,
  'html':               RDF.HTML,
  'json':               CSVW.JSON,
  'number':             XSD.double,
  'xml':                RDF.XMLLiteral,
}


def is_built_in_datatype(value):
    return value in DATATYPES
