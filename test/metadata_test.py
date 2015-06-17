import pprint
from csvwparser import CSVW
from csvwparser import metadata
from csvwparser.metadata import Model

__author__ = 'sebastian'

import unittest


class DanBrickleyCase(unittest.TestCase):
    @unittest.skip("@context appears to be not up-to-date")
    def test_dan_brickley(self):
        testfile = 'csvwparser/testdata/csvw-template/example.csv'
        metafile = 'csvwparser/testdata/csvw-template/example.csv-metadata.json'
        csvw = CSVW(path=testfile, metadata_path=metafile)
        self.assertNotEqual(csvw, None)
        self.assertNotEqual(csvw.metadata, None)
        title = csvw.metadata['dc:title']
        self.assertEqual(title, "My Spreadsheet")
        # TODO write tests

    def test_positive_context(self):
        A = {
            "@context": [ "http://www.w3.org/ns/csvw", { "@language": "en" } ],
            "tables": [{
                "url": "http://example.org/countries.csv",
                "tableSchema": {
                    "columns": [{
                        "name": "countryCode",
                        "datatype": "string",
                        "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                    }, {
                        "name": "latitude",
                        "datatype": "number"
                    }, {
                        "name": "longitude",
                        "datatype": "number"
                    }, {
                        "name": "name",
                        "datatype": "string"
                    }],
                    "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                    "propertyUrl": "http://schema.org/{_name}",
                    "primaryKey": "countryCode"
                }
            }]
        }
        result = metadata.validate(A)
        self.assertTrue(isinstance(result, Model))
        # context is string only
        A = {
            "@context": "http://www.w3.org/ns/csvw",
            "tables": [{
                "url": "http://example.org/countries.csv",
                "tableSchema": {
                    "columns": [{
                        "name": "countryCode",
                        "datatype": "string",
                        "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                    }, {
                        "name": "latitude",
                        "datatype": "number"
                    }, {
                        "name": "longitude",
                        "datatype": "number"
                    }, {
                        "name": "name",
                        "datatype": "string"
                    }],
                    "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                    "propertyUrl": "http://schema.org/{_name}",
                    "primaryKey": "countryCode"
                }
            }]
        }
        result = metadata.validate(A)
        self.assertTrue(isinstance(result, Model))

    def test_negative_context(self):
        # context is missing
        A = {
            "tables": [{
                "url": "http://example.org/countries.csv",
                "tableSchema": {
                    "columns": [{
                        "name": "countryCode",
                        "datatype": "string",
                        "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                    }, {
                        "name": "latitude",
                        "datatype": "number"
                    }, {
                        "name": "longitude",
                        "datatype": "number"
                    }, {
                        "name": "name",
                        "datatype": "string"
                    }],
                    "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                    "propertyUrl": "http://schema.org/{_name}",
                    "primaryKey": "countryCode"
                }
            }]
        }
        result = metadata.validate(A)
        self.assertFalse(result)
        # wrong context
        A = {
            "@context": [ "http://www.w3.org/ns/csvw", { "somethingwrong": "en" } ],
            "tables": [{
                "url": "http://example.org/countries.csv",
                "tableSchema": {
                    "columns": [{
                        "name": "countryCode",
                        "datatype": "string",
                        "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                    }, {
                        "name": "latitude",
                        "datatype": "number"
                    }, {
                        "name": "longitude",
                        "datatype": "number"
                    }, {
                        "name": "name",
                        "datatype": "string"
                    }],
                    "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                    "propertyUrl": "http://schema.org/{_name}",
                    "primaryKey": "countryCode"
                }
            }]
        }
        result = metadata.validate(A)
        self.assertFalse(result)
        # wrong context
        A = {
            "@context": "http://www.w3.org/ns/csv",
            "tables": [{
                "url": "http://example.org/countries.csv",
                "tableSchema": {
                    "columns": [{
                        "name": "countryCode",
                        "datatype": "string",
                        "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                    }, {
                        "name": "latitude",
                        "datatype": "number"
                    }, {
                        "name": "longitude",
                        "datatype": "number"
                    }, {
                        "name": "name",
                        "datatype": "string"
                    }],
                    "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                    "propertyUrl": "http://schema.org/{_name}",
                    "primaryKey": "countryCode"
                }
            }]
        }
        result = metadata.validate(A)
        self.assertFalse(result)

    def test_negative_validate(self):
        # url is missing
        A = {
            "@context": [ "http://www.w3.org/ns/csvw", { "@language": "en" } ],
            "tables": [{
                # "url": "http://example.org/countries.csv",
                "tableSchema": {
                    "columns": [{
                        "name": "countryCode",
                        "datatype": "string",
                        "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                    }, {
                        "name": "latitude",
                        "datatype": "number"
                    }, {
                        "name": "longitude",
                        "datatype": "number"
                    }, {
                        "name": "name",
                        "datatype": "string"
                    }],
                    "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                    "propertyUrl": "http://schema.org/{_name}",
                    "primaryKey": "countryCode"
                }
            }]
        }
        result = metadata.validate(A)
        self.assertFalse(result)

    def test_positive_validate(self):
        self.maxDiff = None
        A = {
            "@context": "http://www.w3.org/ns/csvw",
            "tables": [{
                "url": "http://example.org/countries.csv",
                "tableSchema": {
                  "columns": [{
                    "name": "countryCode",
                    "datatype": "string",
                    "propertyUrl": "http://www.geonames.org/ontology{#_name}"
                  }, {
                    "name": "latitude",
                    "datatype": "number"
                  }, {
                    "name": "longitude",
                    "datatype": "number"
                  }, {
                    "name": "name",
                    "datatype": "string"
                  }],
                  "aboutUrl": "http://example.org/countries.csv{#countryCode}",
                  "propertyUrl": "http://schema.org/{_name}",
                  "primaryKey": "countryCode"
                }
                }, {
                "url": "http://example.org/country_slice.csv",
                "tableSchema": {
                  "columns": [{
                    "name": "countryRef",
                    "valueUrl": "http://example.org/countries.csv{#countryRef}"
                  }, {
                    "name": "year",
                    "datatype": "gYear"
                  }, {
                    "name": "population",
                    "datatype": "integer"
                  }],
                  "foreignKeys": [{
                    "columnReference": "countryRef",
                    "reference": {
                      "resource": "http://example.org/countries.csv",
                      "columnReference": "countryCode"
                    }
                  }]
                }
            }]
        }
        result = metadata.validate(A)
        self.assertTrue(isinstance(result, Model))
        json_res = result.json()
        print json_res
        self.assertEqual(json_res, A)

    def test_normalize(self):
        self.maxDiff = None
        A = {
          "@context": [ "http://www.w3.org/ns/csvw", { "@language": "en" } ],
          "@type": "Table",
          "url": "http://example.com/table.csv",
          "dc:title": [
            "The title of this Table",
            {"@value": "Der Titel dieser Tabelle", "@language": "de"}
          ]
        }
        norm = {
          "@context": "http://www.w3.org/ns/csvw",
          "tables": [
              {
                  "@type": "Table",
                  "url": "http://example.com/table.csv",
                  "dc:title": [
                    {"@value": "The title of this Table", "@language": "en"},
                    {"@value": "Der Titel dieser Tabelle", "@language": "de"}
                  ]
              }
          ],
        }
        val = metadata.validate(A)
        #print val.json()
        #self.assertEqual(val.json(), A)
        val.normalize()
        json_res = val.json()
        print json_res
        self.assertEqual(json_res, norm)

    def test_normalize2(self):
        self.maxDiff = None
        A = {
              "@context": [ "http://www.w3.org/ns/csvw", { "@base": "http://example.com/" } ],
              "@type": "Table",
              "url": "table.csv",
              "schema:url": {"@id": "table.csv"}
        }
        norm = {
              "@context": "http://www.w3.org/ns/csvw",
              "tables": [
                  {
                      "@type": "Table",
                      "url": "http://example.com/table.csv",
                      "schema:url": {"@id": "http://example.com/table.csv"}
                  }
              ]
        }
        val = metadata.validate(A)
        #print val.json()
        #self.assertEqual(val.json(), A)
        val.normalize()
        json_res = val.json()
        print json_res
        self.assertEqual(json_res, norm)

    def test_merge(self):
        self.maxDiff = None
        A = {
          "@context": ["http://www.w3.org/ns/csvw", {"@language": "en",
                                                     "@base": "http://example.com/"}
                       ],
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
          "@context": "http://www.w3.org/ns/csvw",
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
        norm_a = metadata.normalize(A)
        norm_b = metadata.normalize(B)
        pprint.pprint(norm_a.json())
        pprint.pprint(norm_b.json())

        result = metadata.merge([norm_a, norm_b])
        pprint.pprint(result.json())
        self.assertEqual(merged, result.json())


if __name__ == '__main__':
    unittest.main()
