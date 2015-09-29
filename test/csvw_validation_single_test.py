import unittest
import urlparse
from csvw_validation_test_cases import get_manifest, BASE, test_generator, CSVWValidationTestCases, test_generator_metadata

__author__ = 'sebastian'

if __name__ == '__main__':
    test_no = input('Test No.: ')
    test_id = '#test' + str(test_no).zfill(3)
    manifest = get_manifest()
    for i, t in enumerate(manifest['entries']):
        if t['id'].endswith(test_id):
            test_name = ' '.join(['test', t['id'], t['type'], t['name']])
            action_url = t['action']
            action_url = urlparse.urljoin(BASE, action_url)
            implicit = []
            if 'implicit' in t:
                for f in t['implicit']:
                    implicit.append(urlparse.urljoin(BASE, f))

            if 'metadata' in t['option']:
                t['option']['metadata'] = urlparse.urljoin(BASE, t['option']['metadata'])

            if action_url.endswith('.csv'):
                test = test_generator(action_url, implicit, t['type'], t['option'])
                setattr(CSVWValidationTestCases, test_name, test)
            elif action_url.endswith('.json'):
                test = test_generator_metadata(action_url, implicit, t['type'], t['option'])
                setattr(CSVWValidationTestCases, test_name, test)
            break

    unittest.main()
