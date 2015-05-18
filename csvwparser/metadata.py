import urllib2
from pyld import jsonld
import json

CONTEXT = 'http://www.w3.org/ns/csvw.jsonld'

__author__ = 'sebastian'


def validate(metadata):
    compacted = jsonld.compact(metadata, json.load(urllib2.urlopen(CONTEXT)))
    expanded = jsonld.expand(compacted)
    print json.dumps(expanded, indent=2)
    print
    normalized = jsonld.normalize(compacted, {'format': 'application/nquads'})
    print normalized
    return compacted

