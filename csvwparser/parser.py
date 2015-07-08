__author__ = 'neumaier'

def parse(table, url):
    # http://w3c.github.io/csvw/syntax/index.html#parsing

    t = Table(url)
    m = {
        "@context": "http://www.w3.org/ns/csvw",
        "rdfs:comment": [],
        "tableSchema": {
            "columns": []
        }
    }
    if url:
        m['url'] = url

    source_row_number = 1


#def parse(doc, url):
#    datatables = tablemagician.from_file_object(doc)
#    for table in datatables:
#        _parse(table, url)


class Table:
    def __init__(self, url):
        self.columns = []
        self.rows = []
        self.id = None
        self.url = url
        self.table_direction = 'auto'
        self.suppress_output = False
        self.notes = False
        self.foreign_keys = []
        self.transformations = []

