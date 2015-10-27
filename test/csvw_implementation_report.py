from csvw_validation_test_cases import implementation_report

__author__ = 'sebastian'
import rdflib
from rdflib.namespace import FOAF
EARL = rdflib.Namespace("http://www.w3.org/ns/earl#")



class ImplementationReport():
    def __init__(self):
        self.g = rdflib.Graph()
        self.g.parse(location='test/doap.ttl', format='turtle')
        for person in self.g.subjects(rdflib.RDF.type, FOAF.Person):
            self.assertor = person
            break
        for subj in self.g.subjects(rdflib.RDF.type, EARL.TestSubject):
            self.subject = subj
            break

    def run_validation_test(self):
        implementation_report(self.g, self.subject, self.assertor)

    def getResult(self):
        return self.g.serialize(format='turtle')


if __name__ == '__main__':
    rep = ImplementationReport()
    rep.run_validation_test()
    res = rep.getResult()
    print res
    with open('earl.ttl', 'w') as f:
        f.write(res)
