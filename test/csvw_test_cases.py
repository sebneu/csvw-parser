import urlparse
import traceback
import unittest
import json
from csvwparser import CSVW
import urllib2

MAX_TESTS = 5
MANIFEST = 'http://w3c.github.io/csvw/tests/manifest-validation.jsonld'
BASE = 'http://w3c.github.io/csvw/tests/'
TYPES = {
    'csvt:WarningValidationTest': True,
    'csvt:PositiveValidationTest': True,
    'csvt:NegativeValidationTest': False
}


def get_manifest():
    response = urllib2.urlopen(MANIFEST)
    return json.loads(response.read())


class CSVWValidationTestCases(unittest.TestCase):
        pass


def test_generator(csv_file, implicit, type, option):
    def test(self):
        metadata = None
        if 'metadata' in option:
            metadata = option['metadata']

        try:
            csvw = CSVW(csv_file, metadata_url=metadata)
        except Exception as e:
            # this should be a negative test
            if TYPES[type]:
                traceback.print_exc()
            self.assertFalse(TYPES[type])
            return

        # if we get here this should be a positive test
        self.assertTrue(TYPES[type])

        # if we can parse it we should at least produce some embedded metadata
        self.assertNotEqual(csvw.metadata, None)



    return test



if __name__ == '__main__':
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        test_name = 'test ' + t['type'] + ': ' + t['name']
        csv_file = t['action']
        csv_file = urlparse.urljoin(BASE, csv_file)
        implicit = []
        if 'implicit' in t:
            for f in t['implicit']:
                implicit.append(urlparse.urljoin(BASE, f))

        if 'metadata' in t['option']:
            t['option']['metadata'] = urlparse.urljoin(BASE, t['option']['metadata'])

        test = test_generator(csv_file, implicit, t['type'], t['option'])
        setattr(CSVWValidationTestCases, test_name, test)

        if i > MAX_TESTS:
            break

    unittest.main()
