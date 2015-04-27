import json
import os
from csvwparser import CSVW

__author__ = 'sebastian'

import unittest


class DanBrickleyCase(unittest.TestCase):
    def test_dan_brickley(self):
        testfile = 'csvwparser/testdata/csvw-template/example.csv'
        metafile = 'csvwparser/testdata/csvw-template/example.csv-metadata.json'
        csvw = CSVW(path=testfile, metadata_path=metafile)
        self.assertNotEqual(csvw, None)
        self.assertNotEqual(csvw.metadata, None)
        title = getattr(csvw.metadata, 'dc:title')
        self.assertEqual(title, "My Spreadsheet")

if __name__ == '__main__':
    unittest.main()
