import json
import pprint
from cStringIO import StringIO
from pycsvw import CSVW


def test():

    t1 = 'GID,On Street,Species,Trim Cycle,Diameter at Breast Ht,Inventory Date,Comments,Protected,KML\n' \
         '1,ADDISON AV,Celtis australis,Large Tree Routine Prune,11,10/18/2010,,,"<Point><coordinates>-122.156485,37.440963</coordinates></Point>"\n' \
         '2,EMERSON ST,Liquidambar styraciflua,Large Tree Routine Prune,11,6/2/2010,,,"<Point><coordinates>-122.156749,37.440958</coordinates></Point>"\n' \
         '6,ADDISON AV,Robinia pseudoacacia,Large Tree Routine Prune,29,6/1/2010,cavity or decay; trunk decay; codominant leaders; included bark; large leader or limb decay; previous failure root damage; root decay;  beware of BEES,YES,"<Point><coordinates>-122.156299,37.441151</coordinates></Point>"'

    m1_dict = {
          "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
          "@id": "http://example.org/tree-ops-ext",
          "url": "tree-ops-ext.csv",
          "dc:title": "Tree Operations",
          "dcat:keyword": ["tree", "street", "maintenance"],
          "dc:publisher": [{
            "schema:name": "Example Municipality",
            "schema:url": {"@id": "http://example.org"}
          }],
          "dc:license": {"@id": "http://opendefinition.org/licenses/cc-by/"},
          "dc:modified": {"@value": "2010-12-31", "@type": "xsd:date"},
          "notes": [{
            "@type": "oa:Annotation",
            "oa:hasTarget": {"@id": "http://example.org/tree-ops-ext"},
            "oa:hasBody": {
              "@type": "oa:EmbeddedContent",
              "rdf:value": "This is a very interesting comment about the table; it's a table!",
              "dc:format": {"@value": "text/plain"}
            }
          }],
          "dialect": {"trim": True},
          "tableSchema": {
            "columns": [{
              "name": "GID",
              "titles": [
                "GID",
                "Generic Identifier"
              ],
              "dc:description": "An identifier for the operation on a tree.",
              "datatype": "string",
              "required": True,
              "suppressOutput": True
            }, {
              "name": "on_street",
              "titles": "On Street",
              "dc:description": "The street that the tree is on.",
              "datatype": "string"
            }, {
              "name": "species",
              "titles": "Species",
              "dc:description": "The species of the tree.",
              "datatype": "string"
            }, {
              "name": "trim_cycle",
              "titles": "Trim Cycle",
              "dc:description": "The operation performed on the tree.",
              "datatype": "string",
              "lang": "en"
            }, {
              "name": "dbh",
              "titles": "Diameter at Breast Ht",
              "dc:description": "Diameter at Breast Height (DBH) of the tree (in feet), measured 4.5ft above ground.",
              "datatype": "integer"
            }, {
              "name": "inventory_date",
              "titles": "Inventory Date",
              "dc:description": "The date of the operation that was performed.",
              "datatype": {"base": "date", "format": "M/d/yyyy"}
            }, {
              "name": "comments",
              "titles": "Comments",
              "dc:description": "Supplementary comments relating to the operation or tree.",
              "datatype": "string",
              "separator": ";"
            }, {
              "name": "protected",
              "titles": "Protected",
              "dc:description": "Indication (YES / NO) whether the tree is subject to a protection order.",
              "datatype": {"base": "boolean", "format": "YES|NO"},
              "default": "NO"
            }, {
              "name": "kml",
              "titles": "KML",
              "dc:description": "KML-encoded description of tree location.",
              "datatype": "xml"
            }],
            "primaryKey": "GID",
            "aboutUrl": "http://example.org/tree-ops-ext#gid-{GID}"
          }
        }
    m1 = StringIO(json.dumps(m1_dict))
    f = StringIO(t1)
    csvw = CSVW(handle=f, metadata_handle=m1, url='http://example.org/tree-ops-ext.csv')
    for col in csvw.table.columns:
        pprint.pprint(col.name)
        pprint.pprint(col.titles)
        pprint.pprint(col.cells)
        for c in col.cells:
            pprint.pprint(c.value)
    pprint.pprint(csvw.table.rows)

    pprint.pprint(csvw.metadata.json())

    csvw.to_json()



if __name__ == '__main__':
    test()