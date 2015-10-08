from csvwparser.parser_exceptions import ParserException

__author__ = 'neumaier'

'''
Settings:
comment prefix
A character that, when it appears at the beginning of a row, indicates that the row is a comment that should be associated as a rdfs:comment annotation to the table. This is set by the commentPrefix property of a dialect description. The default is null, which means no rows are treated as comments. A value other than null may mean that the source numbers of rows are different from their numbers.
delimiter
The separator between cells, set by the delimiter property of a dialect description. The default is ,.
encoding
The character encoding for the file, one of the encodings listed in [encoding], set by the encoding property of a dialect description. The default is utf-8.
escape character
The character that is used to escape the quote character within escaped cells, or null, set by the doubleQuote property of a dialect description. The default is " (such that "" is used to escape " within an escaped cell).
header row count
The number of header rows (following the skipped rows) in the file, set by the header or headerRowCount property of a dialect description. The default is 1. A value other than 0 will mean that the source numbers of rows will be different from their numbers.
line terminators
The characters that can be used at the end of a row, set by the lineTerminators property of a dialect description. The default is [CRLF, LF].
quote character
The character that is used around escaped cells, or null, set by the quoteChar property of a dialect description. The default is ".
skip blank rows
Indicates whether to ignore wholly empty rows (ie rows in which all the cells are empty), set by the skipBlankRows property of a dialect description. The default is false. A value other than false may mean that the source numbers of rows are different from their numbers.
skip columns
The number of columns to skip at the beginning of each row, set by the skipColumns property of a dialect description. The default is 0. A value other than 0 will mean that the source numbers of columns will be different from their numbers.
skip rows
The number of rows to skip at the beginning of the file, before a header row or tabular data, set by the skipRows property of a dialect description. The default is 0. A value greater than 0 will mean that the source numbers of rows will be different from their numbers.
trim
Indicates whether to trim whitespace around cells; may be true, false, start, or end, set by the skipInitialSpace or trim property of a dialect description. The default is false.
'''
SETTINGS = {
    'comment prefix': None,
    'delimiter': ',',
    'encoding': 'utf-8',
    'escape character': '"',
    'header row count': 1,
    'line terminators': ['CRLF', 'LF'],
    'quote character': '"',
    'skip blank rows': False,
    'skip columns': 0,
    'skip rows': 0,
    'trim': False
}


def parse_row(row, settings):
    # http://www.w3.org/TR/2015/WD-tabular-data-model-20150416/#dfn-parse-a-row

    cell_values = []
    current_cell_value = ''
    quoted = False

    for i, char in enumerate(row):
        if char == settings['escape character'] and i + 1 < len(row) and row[i + 1] == settings['quote character']:
            current_cell_value += settings['quote character']
        elif char == settings['escape character'] and settings['escape character'] != settings['quote character'] and i + 1 < len(row):
            current_cell_value += row[i + 1]
        elif char == settings['quote character']:
            if not quoted:
                quoted = True
                if current_cell_value:
                    raise ParserException('Quotation error: ' + row)
            else:
                quoted = False
                if i + 1 < len(row) and row[i + 1] != settings['delimiter']:
                    raise ParserException('Quotation error: ' + row)
        elif char == settings['delimiter']:
            if quoted:
                current_cell_value += settings['delimiter']
            else:
                cell_values.append(current_cell_value.strip())
                current_cell_value = ''
        else:
            current_cell_value += char

    cell_values.append(current_cell_value.strip())
    return cell_values


def parse(handle, url, settings=SETTINGS):
    # http://w3c.github.io/csvw/syntax/index.html#parsing
    rows = handle.read().splitlines()

    T = Table(url)
    M = {
        "@context": "http://www.w3.org/ns/csvw",
        "rdfs:comment": [],
        "tableSchema": {
            "columns": []
        }
    }
    if url:
        M['url'] = url

    source_row_number = 1

    i = 0
    # Repeat the following the number of times indicated by skip rows
    for i in xrange(len(rows)):
        row = rows[i]
        if i >= settings['skip rows']:
            break
        if settings['comment prefix']:
            if row.startswith(settings['comment prefix']):
                com = row.strip(settings['comment prefix']).strip()
                M['rdfs:comment'].append(com)
        elif row.strip():
            M['rdfs:comment'].append(row)
        source_row_number += 1

    j = i
    # Repeat the following the number of times indicated by header row count
    for j in xrange(i, len(rows)):
        row = rows[j]
        if j >= settings['header row count']:
            break
        if settings['comment prefix']:
            if row.startswith(settings['comment prefix']):
                com = row.strip(settings['comment prefix']).strip()
                M['rdfs:comment'].append(com)
        else:
            # Otherwise, parse the row to provide a list of cell values
            cells = parse_row(row, settings)
            # Remove the first skip columns number of values from the list of cell values
            cells = cells[settings['skip columns']:]
            if len(M['tableSchema']['columns']) == 0:
                M['tableSchema']['columns'] = [{'titles': []} for _ in range(len(cells))]
            for cell_i, value in enumerate(cells):
                if value.strip() == '':
                    pass
                else:
                    M['tableSchema']['columns'][cell_i]['titles'].append(value)
        source_row_number += 1

    row_number = 1
    for k in xrange(j, len(rows)):
        row = rows[k]
        source_column_number = 1
        if settings['comment prefix']:
            if row.startswith(settings['comment prefix']):
                com = row.strip(settings['comment prefix']).strip()
                M['rdfs:comment'].append(com)
        else:
            cells = parse_row(row, settings)
            if settings['skip blank rows'] and len(cells) == len([_ for v in cells if v == '']):
                pass
            else:
                R = Row(table=T, number=row_number, source_number=row_number)
                T.rows.append(R)
                # Remove the first skip columns number of values from the list of cell values
                cells = cells[settings['skip columns']:]
                source_column_number += settings['skip columns']
                # For each of the remaining values at index i in the list of cell values (where i starts at 1)
                for index, value in enumerate(cells):
                    i = index + 1
                    # Identify the column C at index i within the columns of table T. If there is no such column
                    if len(T.columns) < i:
                        C = Column(table=T, number=i, source_number=source_column_number)
                        T.columns.append(C)
                    else:
                        C = T.columns[index]
                    D = Cell(value=value, table=T, column=C, row=R)
                    C.cells.append(D)
                    R.cells.append(D)
                    source_column_number += 1

            source_row_number += 1
        row_number += 1
    # If M.rdfs:comment is an empty array, remove the rdfs:comment property from M
    if not M['rdfs:comment']:
        M.pop('rdfs:comment')

    # Return the table T and the embedded metadata M
    return T, M


class Cell:
    def __init__(self, value, table, column, row):
        self.table = table
        self.column = column
        self.row = row
        self.string_value = value
        self.value = value
        self.errors = []
        self.text_direction = 'ltr'
        self.about_url = None
        self.property_url = None
        self.value_url = None

    def __repr__(self):
        return 'C' + str(self.row) + str(self.column)


class Column:
    def __init__(self, table, number, source_number):
        self.table = table
        self.number = number
        self.source_number = source_number
        self.name = None
        self.titles = []
        self.datatype = basestring
        self.virtual = False
        self.suppress_output = False
        self.cells = []

    def __repr__(self):
        return 'C' + str(self.number)


class Row:
    def __init__(self, table, number, source_number):
        self.table = table
        self.number = number
        self.source_number = source_number
        self.primary_key = []
        self.referenced_rows = []
        self.cells = []

    def __repr__(self):
        return 'R' + str(self.number)

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
