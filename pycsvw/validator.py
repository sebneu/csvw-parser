from StringIO import StringIO
import urllib2
import logging
import json
import simplejson
from pycsvw import metadata
from pycsvw import json_generator
from pycsvw import parser
import metadata_extractor

def validate_file(csv_file_path, schema_file_path):
    csv_handle = open(csv_file_path, 'rb')
    schema_handle = open(schema_file_path, 'rb')
    return validate_handle(csv_handle, schema_handle)
    

def validate_handle(csv_handle, schema_handle):
    table, embedded_schema = parser.parse(csv_handle, None)
    schema = simplejson.load(schema_handle)
    
    valid, error_message = validate_columns_name(embedded_schema, schema)
    if valid:
        return validate_table_data(table, schema)
    else:
        return valid, error_message

def validate_columns_name(embedded_schema, schema):
    columns_in_table = embedded_schema["tableSchema"]["columns"]
    columns_in_schema = schema["tableSchema"]["columns"]
    
    valid = True;    
    error_message = ""
    if len(columns_in_schema) != len(columns_in_table):
        error_message = error_message + "Column number mismatch! Csv has %s columns, but schema has %s columns.\n" % (len(columns_in_table), len(columns_in_schema))
        valid = valid and False                                                                                                                         
    
    for i, column in enumerate(columns_in_schema):
        if "name" in column and not column["name"] in columns_in_table[i]["titles"]:
            error_message = error_message + "Column: %s defined in schema, but not found in csv table!\n" % column["name"]
            valid = valid and False
        
    return (valid, error_message)

def validate_table_data(table, schema):
    columns_in_schema = schema["tableSchema"]["columns"]
    
    valid = True;    
    error_message = ""                                                                                                                  
    
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if not cell.value:
                column = columns_in_schema[i]
                if "required" in column and column["required"]==True:
                    error_message = error_message + "Error in Cell %s:  Column %s is required!\n" % (str(cell), column["name"])
                    valid = valid = valid and False
        
    return (valid, error_message)


def test_validate():
    table_path = "F:\WorkRecord\Feature\MCT\CsvSchema\AdyenAcquirerCode.csv"
    schema_path = "F:\WorkRecord\Feature\MCT\CsvSchema\AdyenAcquirerCode.schema"
    (ret, error_message) = validate_file(table_path, schema_path)
    print("Is valid: %s\nError message: \n%s\n" % (ret, error_message))
          

    
if __name__ == '__main__':
    test_validate()

