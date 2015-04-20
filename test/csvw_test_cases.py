__author__ = 'sebastian'

import unittest
from csvwparser import CSVW


class CSVWTestCases(unittest.TestCase):
    def test_positive_validation(self):
        # TODO read test cases from manifest.csv

        test001 = 'http://w3c.github.io/csvw/tests/test001.csv'
        csvw = CSVW(test001)
        self.assertNotEqual(csvw, None)
        self.assertNotEqual(csvw.metadata, None)

if __name__ == '__main__':
    unittest.main()
