from uritemplate import expand


def generate_object(row, metadata):
    obj = {}




def minimal_mode(table, metadata):
    A = []
    if not metadata.get('suppressOutput', False):
        for row in table.rows:
            obj = generate_object(row, metadata)

