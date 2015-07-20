__author__ = 'sebastian'


def generate_objects(row):
    if 'aboutUrl' in metadata:
        subject = metadata['aboutUrl']


def minimal_mode(table, metadata):
    A = []

    for row in table.rows:
        generate_objects(row)

