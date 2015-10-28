import urlparse
import traceback
import unittest
import json
from StringIO import StringIO
import datetime
import rdflib
from csvwparser import CSVW, metadata
import urllib2

MAX_TESTS = -1
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


def test_generator(csv_url, implicit, type, option):
    def test(self):
        metadata = option.get('metadata')

        try:
            csvw = CSVW(url=csv_url, metadata_url=metadata)
        except Exception as e:
            # this should be a negative test
            if TYPES[type]:
                raise e
            self.assertFalse(TYPES[type])
            return

        # if we get here this should be a positive test
        self.assertTrue(TYPES[type])

        # if we can parse it we should at least produce a table and some embedded metadata
        self.assertNotEqual(csvw.table, None)
        self.assertNotEqual(csvw.metadata, None)

        result_table = csvw.table
        result_meta = csvw.metadata.json()

    return test

def test_generator_metadata(metadata_url, implicit, type, option):
    def test(self):
        csv_url = None
        if implicit:
            for url in implicit:
                if url.endswith('.csv'):
                    csv_url = url
                    break

        if csv_url:
            try:
                csvw = CSVW(url=csv_url, metadata_url=metadata_url)
            except Exception as e:
                # this should be a negative test
                if TYPES[type]:
                    raise
                self.assertFalse(TYPES[type])
                return
            self.assertTrue(TYPES[type])
            self.assertNotEqual(csvw.table, None)
            self.assertNotEqual(csvw.metadata, None)

            result_table = csvw.table
            result_meta = csvw.metadata.json()

        else:
            try:
                url_resp = urllib2.urlopen(metadata_url)
                handle = StringIO(url_resp.read())
                meta = json.load(handle)
                meta_model = metadata.normalize(meta)
            except Exception as e:
                if TYPES[type]:
                    raise e
                self.assertFalse(TYPES[type])
                return
            self.assertTrue(TYPES[type])

            self.assertNotEqual(meta_model, None)
            result_meta = meta_model.json()

    return test




def get_test_method(i, t):
    action_url = t['action']
    action_url = urlparse.urljoin(BASE, action_url)
    implicit = []
    if 'implicit' in t:
        for f in t['implicit']:
            implicit.append(urlparse.urljoin(BASE, f))

    if 'metadata' in t['option']:
        t['option']['metadata'] = urlparse.urljoin(BASE, t['option']['metadata'])

    test = None
    if action_url.endswith('.csv'):
        test = test_generator(action_url, implicit, t['type'], t['option'])
    elif action_url.endswith('.json'):
        test = test_generator_metadata(action_url, implicit, t['type'], t['option'])
    return test


def implementation_report(graph, subject, assertor):
    from rdflib.namespace import XSD, DC, FOAF
    EARL = rdflib.Namespace("http://www.w3.org/ns/earl#")

    validation_html = "http://w3c.github.io/csvw/tests/"
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        # add the properties for a test case
        assertion = rdflib.BNode()
        graph.add( (assertion, rdflib.RDF.type, EARL.Assertion) )
        graph.add( (assertion, EARL.assertedBy, assertor) )
        graph.add( (assertion, EARL.subject, subject) )
        graph.add( (assertion, EARL.test, rdflib.URIRef(validation_html + t['id'])) )
        result = rdflib.BNode()
        graph.add( (assertion, EARL.result, result) )
        graph.add( (result, rdflib.RDF.type, EARL.TestResult) )
        graph.add( (result, EARL.mode, EARL.automatic) )

        # TODO edit this hack...
        # run test case
        test_name = 'tmp'
        test = get_test_method(i, t)
        setattr(CSVWValidationTestCases, test_name, test)

        suite = unittest.TestSuite()
        suite.addTest(CSVWValidationTestCases(test_name))
        runner = unittest.TextTestRunner()
        test_result = runner.run(suite)

        delattr(CSVWValidationTestCases, test_name)

        # check for failures
        if len(test_result.failures) == 0:
            outcome = EARL.passed
        else:
            outcome = EARL.failed
        graph.add( (result, EARL.outcome, outcome) )

        # add timestamp
        now = datetime.datetime.now().isoformat()
        graph.add( (result, DC.date, rdflib.Literal(now, datatype=XSD.date)))


if __name__ == '__main__':
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        test_name = ' '.join(['test', t['id'], t['type'], t['name']])
        meth = get_test_method(i, t)
        if meth:
            setattr(CSVWValidationTestCases, test_name, meth)
        if 0 < MAX_TESTS < i:
            break

    unittest.main()
