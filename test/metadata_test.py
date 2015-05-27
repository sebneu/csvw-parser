from csvwparser import CSVW
from csvwparser import metadata

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
        self.assertTrue(result)
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
        self.assertTrue(result)

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
        self.assertTrue(result)


    @unittest.skip("normalize not implemented")
    def test_normalize(self):
        A = {
          "@context": [ "http://www.w3.org/ns/csvw", { "@language": "en" } ],
          "@type": "Table",
          "url": "http://example.com/table.csv",
          "tableSchema": [],
          "dc:title": [
            "The title of this Table",
            {"@value": "Der Titel dieser Tabelle", "@language": "de"}
          ]
        }
        norm = {
          "@type": "Table",
          "url": "http://example.com/table.csv",
          "tableSchema": [],
          "dc:title": [
            {"@value": "The title of this Table", "@language": "en"},
            {"@value": "Der Titel dieser Tabelle", "@language": "de"}
          ]
        }
        result = metadata.normalize(A)
        self.assertEqual(result, norm)

    @unittest.skip("merge not implemented")
    def test_merge(self):
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
        norm_a = metadata.normalize(A)
        norm_b = metadata.normalize(B)

        result = metadata.merge([norm_a, norm_b])
        self.assertEqual(merged, result)


if __name__ == '__main__':
    unittest.main()
