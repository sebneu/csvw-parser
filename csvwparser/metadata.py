import re
import logger

BASE_URL = None
LANGUAGE = None

class Option:
    Required, NonEmpty = range(2)


class MetaObject:
    def evaluate(self, meta, line=None):
        return False


class Property(MetaObject):
    def __init__(self):
        self.value = None


class Uri(Property):
    def evaluate(self, meta, line=None):
        # TODO
        logger.debug(line, 'URI property: ' + meta)
        result = Uri()
        result.value = meta
        return result


class ColumnReference(Property):

    def evaluate(self, meta, line=None):
        result = ColumnReference()
        if isinstance(meta, basestring):
            # TODO  must match the name on a column description object
            logger.debug(line, 'Column Reference property: ' + meta)
            result.value = meta
            return result
        elif isinstance(meta, list):
            if not meta:
                logger.warning(line, 'the supplied value is an empty array')
                return result
            for m in meta:
                if isinstance(m, basestring):
                    # TODO must match the name on a column description object
                    pass
                else:
                    logger.warning(line, 'the values in the supplied array are not strings: ' + str(meta))
                result.value = meta
                return result

            # TODO  must match the name on a column description object
            logger.debug(line, 'Column Reference property: ' + meta)
            result.value = meta
            return result
        else:
            logger.warning(line, 'the supplied value is not a string or array: ' + str(meta))
            return result


class NaturalLanguage(Property):

    def evaluate(self, meta, line=None):
        # strings
        # arrays
        # objects
        # TODO
        logger.debug(line, 'Natural language property: ' + meta)
        result = NaturalLanguage()
        result.value = meta
        return result


class Link(Property):
    def __init__(self, link_type):
        Property.__init__(self)
        self.link_type = link_type

    def evaluate(self, meta, line=None):
        result = Link(self.link_type)
        if isinstance(meta, basestring):
            if self.link_type == '@id':
                # @id must not start with _:
                if meta.startswith('_:'):
                    logger.error(line, '@id must not start with _:')
                    return False
            logger.debug(line, 'Link property: (' + self.link_type + ': ' + meta + ')')
            result.value = meta
            return result
        else:
            # TODO issue a warning and set prop none
            logger.warning(line, 'value of link property is not a string: ' + str(meta))
            return result


class Array(Property):
    def __init__(self, arg):
        Property.__init__(self)
        self.arg = arg

    def evaluate(self, meta, line=None):
        result = Array(self.arg)
        if isinstance(meta, list):
            # if the arg is a operator, it should take a list as argument
            result.value = self.arg.evaluate(meta, line)
            if result.value:
                return result
        # the meta obj should be a list
        return False


class Common(Property):
    def __init__(self, prop):
        Property.__init__(self)
        self.prop = prop

    def evaluate(self, meta, line=None):
        # TODO
        logger.debug(line, 'CommonProperty: (' + self.prop + ':' + meta + ')')
        result = Common(self.prop)
        result.value = meta
        return result

'''
def normalize(self, value, default_language):
    if isinstance(value, list):
        norm_list = []
        for v in value:
            norm_list.append(self.normalize(v, default_language))
        value = norm_list
    elif isinstance(value, basestring):
        value = {'@value': value}
        if default_language:
            value['@language'] = default_language
    elif isinstance(value, dict) and '@value' in value:
        pass
    elif isinstance(value, dict):
        for k in value:
            if k == '@id':
                # TODO expand any prefixed names and resolve its value against the base URL
                pass
            elif k == '@type':
                pass
            else:
                k[value] = self.normalize(k[value], default_language)
    return value
'''


class Base(Property):
    def evaluate(self, meta, line=None):
        if '@base' in meta:
            result = Base()
            result.value = meta
            return result
        else:
            return False


class Language(Property):
    def evaluate(self, meta, line=None):
        if '@language' in meta:
            result = Language()
            result.value = meta
            return result
        else:
            return False


class Atomic(Property):
    def __init__(self, arg):
        Property.__init__(self)
        self.arg = arg

    def evaluate(self, meta, line=None):
        result = Atomic(self.arg)
        if isinstance(self.arg, MetaObject):
            # a predefined type or an operator

            result.value = self.arg.evaluate(meta, line)
            if result.value:
                return result
        else:
            # numbers, interpreted as integers or doubles
            # booleans, interpreted as booleans (true or false)
            # strings, interpreted as defined by the property
            # objects, interpreted as defined by the property
            # arrays, lists of numbers, booleans, strings, or objects
            # TODO
            if meta == self.arg:
                result.value = meta
                return result
        return False


class Object(Property):
    def __init__(self, dict_obj, inherited_obj=None, common_properties=False):
        Property.__init__(self)
        self.dict_obj = dict_obj
        self.inherited_obj = inherited_obj
        self.common_properties = common_properties

    def evaluate(self, meta, line=None):
        result = Object(self.dict_obj, self.inherited_obj, self.common_properties)
        if isinstance(self.dict_obj, dict) and isinstance(meta, dict):
            if self.inherited_obj:
                self.dict_obj = self.dict_obj.copy()
                self.dict_obj.update(self.inherited_obj)
            # arg is a new schema to validate the metadata
            result.value = _validate(line, meta, self.dict_obj, self.common_properties)
            if result.value:
                return result
        # logger.error(line, 'object property is not a dictionary: ' + str(meta))
        return False


class Operator(MetaObject):
    pass


class BoolOperator(Operator):
    pass


class OfType(Operator):
    def __init__(self, base_type):
        self.base_type = base_type

    def evaluate(self, meta, line=None):
        if isinstance(meta, self.base_type):
            return meta
        return False


class AllDiff(BoolOperator):
    def __init__(self, arg):
        self.arg = arg

    def evaluate(self, meta_list, line=None):
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


class Or(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta, line=None):
        # two types of or: on a list or a value
        if isinstance(meta, list):
            valid = False
            props = []
            for v in self.values:
                if isinstance(v, BoolOperator) and not v.evaluate(meta, line):
                    return False
                prop = v.evaluate(meta, line)
                if prop:
                    valid = True
                    if isinstance(prop, list):
                        props += prop
                    else:
                        props.append(prop)
            if valid:
                return props
            return False
        else:
            for v in self.values:
                if isinstance(v, BoolOperator) and not v.evaluate(meta, line):
                    return False
                prop = v.evaluate(meta, line)
                if prop:
                    return prop
            return False


class And(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta, line=None):
        props = []
        for v in self.values:
            if isinstance(v, BoolOperator):
                if not v.evaluate(meta, line):
                    return False
            else:
                prop = v.evaluate(meta, line)
                if not prop:
                    return False
                if isinstance(prop, list):
                    props += prop
                else:
                    props.append(prop)
        return props


class All(Operator):
    """
    All operator
    Takes a Type in constructor.
    On evaluation, checks if all given items have the given type.
    """
    def __init__(self, typ):
        self.typ = typ

    def evaluate(self, meta_list, line=None):
        props = []
        for meta in meta_list:
            prop = self.typ.evaluate(meta, line)
            if not prop:
                return False
            if isinstance(prop, list):
                props += prop
            else:
                props.append(prop)
        return props


class Some(Operator):
    """
    Some operator
    Takes a Type in constructor.
    On evaluation, checks if some of given items have the given type.
    """
    def __init__(self, typ):
        self.typ = typ
    def evaluate(self, meta_list, line=None):
        props = []
        valid = False
        for meta in meta_list:
            prop = self.typ.evaluate(meta, line)
            if prop:
                valid = True
                if isinstance(prop, list):
                    props += prop
                else:
                    props.append(prop)
        if valid:
            return props
        return False


class Selection(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta, line=None):
        prop = False
        for v in self.values:
            tmp = v.evaluate(meta, line)
            if tmp and prop:
                # already the second match
                logger.debug(line, '(Selection Operator) Only one match allowed: ' + str(meta))
                return False
            if tmp:
                prop = tmp
        # if we get here, we found zero or one match
        return prop


DATATYPE = {
    'TODO': {
        'options': [],
        'type': Atomic('TODO')
    },
    # TODO datatype description object
}

INHERITED = {
    'aboutUrl': {
        'options': [],
        'type': Uri()
    },
    'datatype': {
        'options': [],
        'type': Atomic(Or(OfType(basestring), Object(DATATYPE)))
    },
    'default': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': ''
    },
    'lang': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': 'und'
    },
    'null': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': ''
    },
    'ordered': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    'propertyUrl': {
        'options': [],
        'type': Uri()
    },
    'required': {
        'options': [],
        'type': Atomic(OfType(bool)),
        'default': False
    },
    'separator': {
        'options': [],
        'type': Atomic(OfType(basestring))
    },
    'textDirection': {
        'options': [],
        'type': Atomic(Or('ltr', 'rtl')),
        'default': 'ltr'
    },
    'valueUrl': {
        'options': [],
        'type': Uri()
    }
}

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
            'resource': {
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
        'type': Array(And(All(Object(COLUMN, inherited_obj=INHERITED, common_properties=True)),
                          AllDiff('name')))
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


CONTEXT = Selection(Atomic('http://www.w3.org/ns/csvw'),
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
        'type': Object(SCHEMA, inherited_obj=INHERITED, common_properties=True)
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
        'type': Array(All(Object(TABLE, inherited_obj=INHERITED, common_properties=True)))
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
        'type': Object(SCHEMA, inherited_obj=INHERITED, common_properties=True)
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


def is_common_property(prop):
    return re.match('[a-zA-Z]:[a-zA-Z]', prop)


def _validate(line, meta, schema, common_properties):
    model = {}
    for prop in meta:
        value = meta[prop]
        if prop in schema:
            opts = schema[prop]['options']
            t = schema[prop]['type']
            # check if not empty
            if value:
                prop_eval = t.evaluate(value, line)
                if not prop_eval:
                    return False
                model[prop] = prop_eval
            elif Option.NonEmpty in opts:
                logger.debug(line, 'Property is empty: ' + prop)
                return False
        elif common_properties and is_common_property(prop):
            prop_eval = Common(prop).evaluate(value, line)
            if not prop_eval:
                return False
            model[prop] = prop_eval
        else:
            logger.warning(line, 'Unknown property: ' + prop)
            model[prop] = prop
    # check for missing props
    for prop in schema:
        if Option.Required in schema[prop]['options'] and prop not in meta:
            logger.error(line, 'Property missing: ' + prop)
            return False
    return model


def validate(metadata):
    # outer_group = Or(Object(TABLE_GROUP), Object(TABLE))
    outer_group = Object(TABLE_GROUP, inherited_obj=INHERITED, common_properties=True)
    model = outer_group.evaluate(metadata)
    return model


def _normalize(meta, schema, default_language):
    for prop in meta:
        value = meta[prop]
        if is_common_property(prop) or prop == 'notes':
            meta[prop] = Common(prop).normalize(value, default_language)
        elif prop in schema:
            t = schema[prop]['type']
            meta[prop] = t.normalize(value, default_language)



def normalize(metadata, default_language=None):
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
    outer_group = Object(TABLE_GROUP, inherited_obj=INHERITED, common_properties=True)
    return outer_group.normalize(metadata)


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
