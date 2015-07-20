import pprint
from cStringIO import StringIO
from csvwparser import CSVW


def test():

    t1 = 'countryCode,latitude,longitude,name\n' \
         'AD,42.546245,1.601554,Andorra\n' \
         'AE,23.424076,53.847818,"United Arab Emirates"\n' \
         'AF,33.93911,67.709953,Afghanistan'
    f = StringIO(t1)
    csvw = CSVW(handle=f, url='http://example.org/countries.csv')
    for col in csvw.table.columns:
        pprint.pprint(col.name)
        pprint.pprint(col.titles)
        pprint.pprint(col.cells)
        for c in col.cells:
            pprint.pprint(c.value)
    pprint.pprint(csvw.table.rows)


    pprint.pprint(csvw.metadata.json())


if __name__ == '__main__':
    test()