import json
import os
import urllib2
from pyld import jsonld
from csvwparser import CSVW
from csvwparser import metadata_extractor

__author__ = 'sebastian'

import unittest


class DanBrickleyCase(unittest.TestCase):
    def test_dan_brickley(self):
        testfile = 'csvwparser/testdata/csvw-template/example.csv'
        metafile = 'csvwparser/testdata/csvw-template/example.csv-metadata.json'
        csvw = CSVW(path=testfile, metadata_path=metafile)
        self.assertNotEqual(csvw, None)
        self.assertNotEqual(csvw.metadata, None)
        title = csvw.metadata['dc:title']
        self.assertEqual(title, "My Spreadsheet")


    def test_metadata_merge(self):
        CONTEXT = 'http://www.w3.org/ns/csvw.jsonld'
        A = {
          "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
          "tables": [{
            "url": "doc1.csv",
            "dc:title": "foo",
            "tableDirection": "ltr",
            "tableSchema": {
              "aboutUrl": "{#foo}",
              "columns": [{
                "name": "foo",
                "titles": "Foo",
                "required": True
              }, {
                "name": "bar"
              }]
            }
          }, {
            "url": "doc2.csv"
          }]
        }

        B = {
          "@context": "http://www.w3.org/ns/csvw",
          "url": "http://example.com/doc1.csv",
          "dc:description": "bar",
          "tableSchema": {
            "propertyUrl": "{#_name}",
            "columns": [{
              "titles": "Foo",
              "required": False
            }, {
              "name": "bar"
            }, {
            }]
          }
        }

        merged = {
          "tables": [{
            "url": "http://example.com/doc1.csv",
            "dc:title": {"@value": "foo", "@language": "en"},
            "dc:description": {"@value": "bar"},
            "tableDirection": "ltr",
            "tableSchema": {
              "aboutUrl": "{#foo}",
              "propertyUrl": "{#_name}",
              "columns": [{
                "name": "foo",
                "titles": { "en": [ "Foo" ]},
                "required": True
              },{
                "name": "bar"
              }]
            }
          }, {
            "url": "http://example.com/doc2.csv"
          }]
        }

        # normalizing a
        context = json.load(urllib2.urlopen(CONTEXT))
        comp_a = jsonld.compact(A, context)
        comp_b = jsonld.compact(B, context)

        result = metadata_extractor.merge_metadata([comp_a, comp_b])
        self.assertEqual(merged, result)


if __name__ == '__main__':
    unittest.main()
