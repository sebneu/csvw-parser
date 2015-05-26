import logger

BASE_URL = None
LANGUAGE = None

class Option:
    Required, NonEmpty = range(2)


class MetaObject:
    pass


class Property(MetaObject):
    pass

    def evaluate(self, meta):
        return True


class ColumnReference(Property):
    def __init__(self):
        pass

    def evaluate(self, meta, line=None):
        if isinstance(meta, basestring):
            # TODO  must match the name on a column description object
            return True
        elif isinstance(meta, list):
            if not meta:
                logger.warning(line, 'the supplied value is an empty array')
                return True
            for m in meta:
                if isinstance(m, basestring):
                    # TODO must match the name on a column description object
                    pass
                else:
                    logger.warning(line, 'the values in the supplied array are not strings: ' + str(meta))
                return True

            # TODO
            pass
        else:
            logger.warning(line, 'the supplied value is not a string or array: ' + str(meta))
            return True

class NaturalLanguage(Property):
    def __init__(self):
        pass

    def evaluate(self, meta):
        # strings
        # arrays
        # objects
        # TODO
        return False


class Link(Property):
    def __init__(self, link_type):
        self.link_type = link_type
    def evaluate(self, meta, line=None):
        if isinstance(meta, basestring):
            if self.link_type == '@id':
                # @id must not start with _:
                logger.error(line, '@id must not start with _:')
                return not meta.startswith('_:')
            return True
        else:
            # TODO issue a warning and return True
            logger.warning(line, 'value of link property is not a string: ' + str(meta))
            return True


class Array(Property):
    def __init__(self, arg):
        self.arg = arg

    def evaluate(self, meta, line=None):
        if isinstance(meta, list):
            # if the arg is a operator, it should take a list as argument
            return self.arg.evaluate(meta)
        else:
            # the meta obj should be a list
            return False


class Base(Property):
    def evaluate(self, meta):
        if '@base' in meta:
            global BASE_URL
            BASE_URL = meta['@base']
            return True
        else:
            return False


class Language(Property):
    def evaluate(self, meta):
        if '@language' in meta:
            global LANGUAGE
            LANGUAGE = meta['@language']
            return True
        else:
            return False

class Atomic(Property):
    def __init__(self, arg):
        self.arg = arg

    def evaluate(self, meta):
        if isinstance(self.arg, MetaObject):
            # a predefined type or an operator
            return self.arg.evaluate(meta)
        else:
            # numbers, interpreted as integers or doubles
            # booleans, interpreted as booleans (true or false)
            # strings, interpreted as defined by the property
            # objects, interpreted as defined by the property
            # arrays, lists of numbers, booleans, strings, or objects
            # TODO
            return meta == self.arg


class Object(Property):
    def __init__(self, arg):
        self.arg = arg
    def evaluate(self, meta, line=None):
        if isinstance(self.arg, dict):
            # arg is a new schema to validate the metadata
            return _validate(line, meta, self.arg)
        else:
            # TODO other types? warning?
            logger.error(line, 'object property is not a dictionary: ' + str(meta))
            return False


class Operator(MetaObject):
    pass


class OfType(Operator):
    def __init__(self, base_type):
        self.base_type = base_type

    def evaluate(self, meta):
        return isinstance(meta, self.base_type)


class Or(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta):
        for v in self.values:
            if isinstance(v, MetaObject) and v.evaluate(meta):
                return True
            elif v == meta:
                return True
        return False


class And(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta):
        for v in self.values:
            if isinstance(v, MetaObject):
                if not v.evaluate(meta):
                    return False
            else:
                if v != meta:
                    return False
        return True


class All(Operator):
    """
    All operator
    Takes a Type in constructor.
    On evaluation, checks if all given items have the given type.
    """
    def __init__(self, typ):
        self.typ = typ
    def evaluate(self, meta_list):
        for meta in meta_list:
            if not self.typ.evaluate(meta):
                return False
        return True


class Some(Operator):
    """
    Some operator
    Takes a Type in constructor.
    On evaluation, checks if some of given items have the given type.
    """
    def __init__(self, typ):
        self.typ = typ
    def evaluate(self, meta_list):
        for meta in meta_list:
            if self.typ.evaluate(meta):
                return True


class AllDiff(Operator):
    def __init__(self, arg):
        self.arg = arg
    def evaluate(self, meta_list):
        values = []
        for meta in meta_list:
            v = None
            if isinstance(meta, dict):
                if self.arg in meta:
                    v = meta[self.arg]
            if isinstance(meta, basestring):
                v = meta
            if v and v in values:
                return False
            values.append(v)
        return True


class XOr(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta, line=None):
        found = False
        for v in self.values:
            if v.evaluate(meta):
                if found:
                    # already the second match
                    logger.debug(line, '(XOr Operator) Only one match allowed: ' + v)
                    return False
                found = True
        # if we get here, we found zero or one match
        return found

COLUMN = {
    'name': {
        'options': [],
        'type': Atomic(OfType(basestring))
    },
    'suppressOutput': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    'titles': {
        'options': [],
        'type': NaturalLanguage()
    },
    'virtual': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    '@id': {
        'options': [],
        'type': Link('@id')
    },
    '@type': {
        'options': [],
        'type': Atomic('Column')
    }
}

FOREIGN_KEY = {
    'columnReference': {
        'options': [Option.Required],
        'type': ColumnReference()
    },
    'reference': {
        'options': [],
        'type': Object({
                'resources': {
                    'options': [],
                    'type': Link('resources')
                },
                'schemaReference': {
                    'options': [],
                    'type': Link('schemaReference')
                },
                'columnReference': {
                    'options': [Option.Required],
                    'type': ColumnReference()
                }
            })
    }
}

SCHEMA = {
    'foreignKeys': {
        'options': [],
        'type': Array(All(Object(FOREIGN_KEY)))
    },
    'columns': {
        'options': [],
        'type': Array(And(All(Object(COLUMN)),
                          AllDiff('name'))
                      )
    },
    'primaryKey': {
        'options': [],
        'type': ColumnReference()
    },
    '@id': {
        'options': [],
        'type': Link('@id')
    },
    '@type': {
        'options': [],
        'type': Atomic('Schema')
    }
}

DIALECT = {
    'encoding': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': 'utf-8'
    },
    'lineTerminators': {
        'options': [],
        'type': Atomic(OfType(list)),
        'default': ["\r\n", "\n"]
    },
    'quoteChar': {
        'options': [],
        'type': Atomic(Or(OfType(basestring), None)),
        'default': '"'
    },
    'doubleQuote': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': True
    },
    'skipRows': {
        'options': [],
        'type': Atomic(OfType(int)),
        'default': 0
    },
    'commentPrefix': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': '#'
    },
    'header': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': True
    },
    'headerRowCount': {
        'options': [],
        'type': Atomic(OfType(int)),
        'default': 1
    },
    'delimiter': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': ','
    },
    'skipColumns': {
        'options': [],
        'type': Atomic(OfType(int)),
        'default': 0
    },
    'skipBlankRows': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    'skipInitialSpace': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    'trim': {
        'options': [],
        'type': Atomic(Or('true', 'false', 'start', 'end')),
        'default': 'false'
    },
    '@id': {
        'options': [],
        'type': Link('@id')
    },
    '@type': {
        'options': [],
        'type': Atomic('Dialect')
    }
}



TRANSFORMATION = {
    'url' : {
        'options': [Option.Required],
        'type': Link('url')
    },
    'targetFormat': {
        'options': [Option.Required],
        'type': Link('targetFormat')
    },
    'scriptFormat': {
        'options': [Option.Required],
        'type': Link('scriptFormat')
    },
    'titles': {
        'options': [],
        'type': NaturalLanguage()
    },
    'source': {
        'options': [],
        'type': Atomic(OfType(basestring))
    },
    '@id': {
        'options': [],
        'type': Link('@id')
    },
    '@type': {
        'options': [],
        'type': Atomic('Template')
    }
}


CONTEXT = XOr(Atomic('http://www.w3.org/ns/csvw'),
              Array(And(Some(Atomic('http://www.w3.org/ns/csvw')),
                        Some(Or(Atomic(Base()), Atomic(Language()))))
                    )
              )

TABLE = {
    'url': {
        'options': [Option.Required],
        'type': Link('url')
    },
    'transformations': {
        'options': [],
        'type': Array(All(Object(TRANSFORMATION)))
    },
    'tableDirection': {
        'options': [],
        'type': Atomic(Or('rtl', 'ltr', 'default'))
    },
    'tableSchema': {
        'options': [],
        'type': Object(SCHEMA)
    },
    'dialect': {
        'options': [],
        'type': Object(DIALECT)
    },
    'notes': {
        'options': [],
        'type': Array(Property())
    },
    'suppressOutput': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    '@id': {
        'options': [],
        'type': Link('@id')
    },
    '@type': {
        'options': [],
        'type': Atomic('Table')
    },
    '@context': {
        'options': [],
        'type': CONTEXT
    }
}


TABLE_GROUP = {
    '@context': {
        'options': [Option.Required],
        'type': CONTEXT
    },
    'tables': {
        'options': [Option.Required, Option.NonEmpty],
        'type': Array(All(Object(TABLE)))
    },
    'transformations': {
        'options': [],
        'type': Array(All(Object(TRANSFORMATION)))
    },
    'tableDirection': {
        'options': [],
        'type': Atomic(Or('rtl', 'ltr', 'default'))
    },
    'tableSchema': {
        'options': [],
        'type': Object(SCHEMA)
    },
    'dialect': {
        'options': [],
        'type': Object(DIALECT)
    },
    'notes': {
        'options': [],
        'type': Array(Property())
    },
    '@id': {
        'options': [],
        'type': Link('@id')
    },
    '@type': {
        'options': [],
        'type': Atomic('TableGroup')
    },
}


def _validate(line, meta, schema):
    for prop in schema:
        # TODO remove this if condition
        #if schema[prop]:
        opts = schema[prop]['options']
        t = schema[prop]['type']
        if prop in meta:
            value = meta[prop]
            # check if not empty
            if value:
                if not t.evaluate(value):
                    return False
            elif Option.NonEmpty in opts:
                logger.debug(line, 'Property is empty: ' + prop)
                return False
        elif Option.Required in opts:
            logger.debug(line, 'Property missing: ' + prop)
            return False
    return True


def validate(metadata):
    outer_group = Or(Object(TABLE_GROUP), Object(TABLE))
    return outer_group.evaluate(metadata)


def normalize(metadata):
    """
    1)If the property is a common property or notes the value must be normalized as follows:
        1.1)If the value is an array, each value within the array is normalized in place as described here.
        1.2)If the value is a string, replace it with an object with a @value property whose value is that string. If a default language is specified, add a @language property whose value is that default language.
        1.3)If the value is an object with a @value property, it remains as is.
        1.4)If the value is any other object, normalize each property of that object as follows:
            1.4.1)If the property is @id, expand any prefixed names and resolve its value against the base URL.
            1.4.2)If the property is @type, then its value remains as is.
            1.4.3)Otherwise, normalize the value of the property as if it were a common property, according to this algorithm.
        1.5)Otherwise, the value remains as is.
    2)If the property is an array property each element of the value is normalized using this algorithm.
    3)If the property is a link property the value is turned into an absolute URL using the base URL.
    4)If the property is an object property with a string value, the string is a URL referencing a JSON document containing a single object. Fetch this URL to retrieve an object, which may have a local @context. Raise an error if fetching this URL does not result in a JSON object. Normalize each property in the resulting object recursively using this algorithm and with its local @context then remove the local @context property. If the resulting object does not have an @id property, add an @id whose value is the original URL. This object becomes the value of the original object property.
    5)If the property is an object property with an object value, normalize each property recursively using this algorithm.
    6)If the property is a natural language property and the value is not already an object, it is turned into an object whose properties are language codes and where the values of those properties are arrays. The suitable language code for the values is determined through the default language; if it can't be determined the language code und must be used.
    7)If the property is an atomic property that can be a string or an object, normalize to the object form as described for that property.
    Following this normalization process, the @base and @language properties within the @context are no longer relevant; the normalized metadata can have its @context set to http://www.w3.org/ns/csvw.
    """
    # TODO
    return metadata


def _merge_in(key, B, A):
        if isinstance(B, list):
            # TODO array property
            return
        if isinstance(B, dict) and isinstance(A, dict):
            for k in B:
                if k in A:
                    _merge_in(k, B[k], A[k])
        if isinstance(B, basestring):
            # TODO check for natural language property
            pass


def merge(meta_sources):
    """
    from highest priority to lowest priority by merging the first two metadata files
    """
    A = None
    for B in meta_sources:
        # check if we are in the first iteration
        if not A:
            A = B
            # finished, because we don't have to to merge B in A
        else:
            # top level of 2 metadata objects is dict
            for k in B:
                if k in A:
                    _merge_in(k, B[k], A)
                else:
                    # if property not in A, just add it
                    A[k] = B[k]
    return A
