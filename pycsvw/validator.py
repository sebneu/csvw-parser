import ntpath
import simplejson
import csv_parser

def validate_file(csv_file_path, schema_file_path):
    csv_handle = open(csv_file_path, 'rb')
    csv_file_name = ntpath.basename(csv_file_path)
    schema_handle = open(schema_file_path, 'rb')
    return validate_handle(csv_handle, csv_file_name, schema_handle)
    

def validate_handle(csv_handle, csv_file_name, schema_handle):
    table, embedded_schema = csv_parser.parse(csv_handle, None)
    schema = simplejson.load(schema_handle)
    tableSchema = None
    if "tables" in schema:
        talbes = schema["tables"]
        for i, current_table in enumerate(talbes):
            if "url" in current_table and current_table["url"] == csv_file_name:
                tableSchema = current_table
                break
    else:
        tableSchema = schema
    
    if not tableSchema:
        return (False, "Could not find schema for table %s: " % csv_file_name )
    
    valid, error_message = validate_columns_name(embedded_schema, tableSchema)
    if valid:
        return validate_table_data(table, tableSchema)
    else:
        return valid, error_message

def validate_columns_name(embedded_schema, schema):
    columns_in_table = embedded_schema["tableSchema"]["columns"]
    columns_in_schema = schema["tableSchema"]["columns"]
    
    valid = True;    
    error_message = ""
    if len(columns_in_schema) != len(columns_in_table):
        error_message += "Column number mismatch! Csv has %s columns, but schema has %s columns.\n" % (len(columns_in_table), len(columns_in_schema))
        return (False, error_message)                                                                                                                         
    
    for i, column in enumerate(columns_in_schema):
        if "name" in column and not column["name"] in columns_in_table[i]["titles"]:
            error_message += "Column: %s defined in schema, but not found in csv table!\n" % column["name"]
            valid = False
        
    return (valid, error_message)

def validate_table_data(table, schema):
    table_schema = schema["tableSchema"]
    columns_in_schema = table_schema["columns"]
    
    valid = True;    
    error_message = ""                                                                                                                  
    pk_value_set = set()

    pk_column_list = list()
    if "primaryKey" in table_schema:
        pk_json = table_schema["primaryKey"]
        if pk_json:
            if isinstance(pk_json, list):
                pk_column_list = pk_json
            else:
                pk_column_list.append(pk_json); 
    pk_column_index_list = get_column_index(columns_in_schema, pk_column_list)

    for row in table.rows:
        # check required
        for i, cell in enumerate(row.cells):
            if not cell.value:
                column = columns_in_schema[i]
                if "required" in column and column["required"]==True:
                    error_message += "Error in %s:  Column %s is required!\n" % (str(cell), column["name"])
                    valid = False
        # check primary key
        if len(pk_column_index_list) > 0:
            pk_value = concatenate_pk_value(row, pk_column_index_list)
            if pk_value in pk_value_set:
                valid = False
                error_message += "Error in %s: duplicated value: %s for primary key columns: %s\n" % (str(row), pk_value, pk_column_list)
            else:
                pk_value_set.add(pk_value)

    return (valid, error_message)

def concatenate_pk_value(row, pk_column_index_list):
    value_list = list()
    for cell in row.cells:
            if cell.column.number in pk_column_index_list:
                value_list.append(cell.value) 
    pk_value_tuple = tuple(value_list)
    return pk_value_tuple

def get_column_index(columns_in_schema, pk_column_list):
    pk_column_index_list = list()
    for i, column in enumerate(columns_in_schema):
        if column["name"] in pk_column_list:
            pk_column_index_list.append(i+1)
    
    return pk_column_index_list


def test_validate():
    table_path = "F:\WorkRecord\Feature\MCT\CsvSchema\AdyenAcquirerCode.csv"
    schema_path = "F:\WorkRecord\Feature\MCT\CsvSchema\AdyenAcquirerCode.schema"
    (ret, error_message) = validate_file(table_path, schema_path)
    print("Is valid: %s\nError message: \n%s\n" % (ret, error_message))
          

    
if __name__ == '__main__':
    test_validate()

