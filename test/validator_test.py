import sys
import unittest
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from pycsvw import validator


class TestCsvValidator(unittest.TestCase):

  def test_validate_csv_pass(self):
      csvPath = os.path.join(parentdir, r"pycsvw/testdata/csvw-template/example.csv")
      schemaPath = os.path.join(parentdir, r"pycsvw/testdata/csvw-template/example.csv-metadata.json")
      (ret, error_message) = validator.validate_file(csvPath, schemaPath)
      self.assertTrue(ret)

  def test_validate_csv_column_missing(self):
      csvPath = os.path.join(parentdir, "pycsvw/testdata/tree-ops.csv")
      schemaPath = os.path.join(parentdir, r"pycsvw/testdata/test124-user-metadata.json")
      expectedResultPath = os.path.join(parentdir, r"pycsvw/testdata/validate-result-missing-column.txt")

      with open(expectedResultPath, 'r') as myfile:
          expectedResult=myfile.read()

      (ret, error_message) = validator.validate_file(csvPath, schemaPath)
      self.assertEqual(expectedResult.rstrip(), error_message.rstrip())

  def test_validate_csv_required_missing(self):
      csvPath = os.path.join(parentdir, "pycsvw/testdata/test125.csv")
      schemaPath = os.path.join(parentdir, r"pycsvw/testdata/test125-metadata.json")
      expectedResultPath = os.path.join(parentdir, r"pycsvw/testdata/validate-result-required-fail.txt")

      with open(expectedResultPath, 'r') as myfile:
          expectedResult=myfile.read()

      (ret, error_message) = validator.validate_file(csvPath, schemaPath)
      self.assertEqual(expectedResult.rstrip(), error_message.rstrip())

  def test_validate_csv_primary_key_fail(self):
      csvPath = os.path.join(parentdir, "pycsvw/testdata/test234.csv")
      schemaPath = os.path.join(parentdir, r"pycsvw/testdata/test234-metadata.json")
      expectedResultPath = os.path.join(parentdir, r"pycsvw/testdata/validate-result-primary-key-fail.txt")

      with open(expectedResultPath, 'r') as myfile:
          expectedResult=myfile.read()

      (ret, error_message) = validator.validate_file(csvPath, schemaPath)
      self.assertEqual(expectedResult.rstrip(), error_message.rstrip())

if __name__ == '__main__':
    unittest.main()
    