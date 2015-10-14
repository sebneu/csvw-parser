import re
from csvwparser.parser_exceptions import ValidationException
import logger
import urlparse
import language_tags


def is_absolute(url):
    return bool(urlparse.urlparse(url).netloc)


def is_common_property(prop):
    return re.match('^[a-zA-Z]*:[a-zA-Z]*$', prop)


class Option:
    Required, NonEmpty = range(2)

class Commands:
    Remove = 'REMOVE'

class MetaObject:
    def evaluate(self, meta, params, default=None, line=None):
        return False


class Property(MetaObject):
    def __init__(self):
        self.value = None

    def normalize(self, params):
        pass

    def merge(self, obj):
        # TODO
        pass
        # print self.value

    def json(self):
        return self.value


class Uri(Property):
    def evaluate(self, meta, params, default=None, line=None):
        # TODO
        logger.debug(line, 'URI property: ' + str(meta))
        result = Uri()
        result.value = meta
        return result


class ColumnReference(Property):

    def evaluate(self, meta, params, default=None, line=None):
        result = ColumnReference()
        if isinstance(meta, basestring):
            # TODO  must match the name on a column description object
            logger.debug(line, 'Column Reference property: ' + str(meta))
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
            logger.debug(line, 'Column Reference property: ' + str(meta))
            result.value = meta
            return result
        else:
            logger.warning(line, 'the supplied value is not a string or array: ' + str(meta))
            return result


class NaturalLanguage(Property):

    def evaluate(self, meta, params, default=None, line=None):
        # strings
        # arrays
        # objects
        # TODO
        if isinstance(meta, dict):
            for k in meta:
                if not language_tags.tags.check(k):
                    logger.error(line, 'Natural language properties MUST be language codes as defined by [BCP47]: ' + str(meta))
                    return False
        logger.debug(line, 'Natural language property: ' + str(meta))
        result = NaturalLanguage()
        result.value = meta
        return result

    def normalize(self, params):
        if isinstance(self.value, list):
            if 'default_language' in params:
                value = {params['default_language']: list(self.value)}
            else:
                value = {'und': list(self.value)}
            self.value = value
        else:
            self.value = self._normalize(self.value, params)

    def _normalize(self, value, params):
        if isinstance(value, basestring):
            value = [value]
            if 'default_language' in params:
                value = {params['default_language']: value}
            else:
                value = {'und': value}
        return value

    def merge(self, obj):
        for k in obj.value:
            # k is a language code of B
            for v in obj.value[k]:
                # values from A followed by those from B that were not already a value in A
                if k in self.value and v not in self.value[k]:
                    self.value[k].append(v)

                #
                if 'und' in self.value and v in self.value['und']:
                    self.value['und'].remove(v)
                    if k not in self.value:
                        self.value[k] = []
                    self.value[k].append(v)
                    if len(self.value['und']) == 0:
                        self.value.pop('und')


class Link(Property):
    def __init__(self, link_type):
        Property.__init__(self)
        self.link_type = link_type

    def evaluate(self, meta, params, default=None, line=None):
        result = Link(self.link_type)
        if isinstance(meta, basestring):
            if self.link_type == '@id':
                # @id must not start with _:
                if meta.startswith('_:'):
                    err_msg = '@id must not start with _:'
                    logger.error(line, err_msg)
                    return False
            logger.debug(line, 'Link property: (' + self.link_type + ': ' + str(meta) + ')')
            result.value = meta
            return result
        else:
            # issue a warning
            logger.warning(line, 'value of link property is not a string: ' + str(meta))
            return result

    def normalize(self, params):
        # turn into absolute url using base url
        if self.value and not is_absolute(self.value) and 'base_url' in params:
            self.value = urlparse.urljoin(params['base_url'], self.value)


class Array(Property):
    def __init__(self, arg, warning_only=False):
        Property.__init__(self)
        self.arg = arg
        self.warning_only = warning_only

    def evaluate(self, meta, params, default=None, line=None):
        result = Array(self.arg)
        if isinstance(meta, list):
            # if the arg is a operator, it should take a list as argument
            result.value = self.arg.evaluate(meta, params, line)
            if result.value:
                return result
        # error while parsing
        if self.warning_only:
            result.value = {}
            return result
        else:
            # the meta obj should be a list
            return False

    def normalize(self, params):
        for v in self.value:
            v.normalize(params)

    def merge(self, obj):
        if isinstance(obj.value, list):
            # TODO maybe wrong??
            for i, v in enumerate(obj.value):
                if len(self.value) > i:
                    self.value[i].merge(v)

    def json(self):
        return [v.json() for v in self.value]


class Common(Property):
    def __init__(self, prop):
        Property.__init__(self)
        self.prop = prop

    def evaluate(self, meta, params, default=None, line=None):
        # TODO http://www.w3.org/TR/2015/WD-tabular-metadata-20150416/#h-values-of-common-properties
        logger.debug(line, 'CommonProperty: (' + str(self.prop) + ')')
        result = Common(self.prop)
        result.value = meta
        return result

    def normalize(self, params):
        self.value = self._normalize(self.value, params)

    def _normalize(self, value, params):
        if isinstance(value, list):
            norm_list = []
            for v in value:
                norm_list.append(self._normalize(v, params))
                value = norm_list
        elif isinstance(value, dict) and '@value' in value:
            pass
        elif isinstance(value, dict):
            for k in value:
                if k == '@id':
                    if not is_absolute(value[k]) and 'base_url' in params:
                        value[k] = urlparse.urljoin(params['base_url'], value[k])
                elif k == '@type':
                    pass
                else:
                    value[k] = self._normalize(value[k], params)
        elif isinstance(value, basestring):
            value = {'@value': value}
            if 'default_language' in params:
                value['@language'] = params['default_language']
        return value


class Base(Property):
    def evaluate(self, meta, params, default=None, line=None):
        if '@base' in meta:
            result = Base()
            result.value = meta['@base']
            params['base_url'] = result.value
            return result
        else:
            return False

    def json(self):
        return {'@base': self.value}


class Language(Property):
    def evaluate(self, meta, params, default=None, line=None):
        if '@language' in meta:
            result = Language()
            result.value = meta['@language']
            params['default_language'] = result.value
            return result
        else:
            return False

    def json(self):
        return {'@language': self.value}


class Atomic(Property):
    def __init__(self, arg):
        Property.__init__(self)
        self.arg = arg

    def evaluate(self, meta, params, default=None, line=None):
        result = Atomic(self.arg)
        if isinstance(self.arg, MetaObject):
            # a predefined type or an operator

            result.value = self.arg.evaluate(meta, params, default, line)
            if result.value == Commands.Remove:
                return Commands.Remove
            elif result.value:
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

    def json(self):
        if isinstance(self.value, MetaObject):
            return self.value.json()
        else:
            return self.value


class Object(Property):
    def __init__(self, dict_obj, inherited_obj=None, common_properties=False, warning_only=False):
        Property.__init__(self)
        self.dict_obj = dict_obj
        self.inherited_obj = inherited_obj
        self.common_properties = common_properties
        self.warning_only = warning_only

    def evaluate(self, meta, params, default=None, line=None):
        result = Object(self.dict_obj, self.inherited_obj, self.common_properties)
        if isinstance(self.dict_obj, dict) and isinstance(meta, dict):
            if self.inherited_obj:
                self.dict_obj = self.dict_obj.copy()
                self.dict_obj.update(self.inherited_obj)
            # arg is a new schema to validate the metadata
            result.value = _validate(line, meta, params, self.dict_obj, self.common_properties)
            if result.value is not False:
                return result
        # logger.error(line, 'object property is not a dictionary: ' + str(meta))
        if self.warning_only:
            logger.warning(line, 'The value of an object property is not a string or object (' + str(meta) + ').'
                                 'An object with no properties is returned.')
            result.value = {}
            return result
        else:
            return False

    def normalize(self, params):
        for prop in self.value:
            self.value[prop].normalize(params)

        if '@context' in self.value:
            p = Atomic('http://www.w3.org/ns/csvw')
            p.value = 'http://www.w3.org/ns/csvw'
            self.value['@context'] = p

    def merge(self, obj):
        for k in obj.value:
            if k in self.value:
                self.value[k].merge(obj.value[k])
            else:
                # if property not in A, just add it
                self.value[k] = obj.value[k]

    def json(self):
        return {k: self.value[k].json() for k in self.value}


class Operator(MetaObject):
    pass


class BoolOperator(Operator):
    pass


class OfType(Operator):
    def __init__(self, base_type, warning_only=False):
        self.base_type = base_type
        self.warning_only = warning_only

    def evaluate(self, meta, params, default=None, line=None):
        if isinstance(meta, self.base_type):
            return meta
        elif self.warning_only:
            logger.warning(line, 'Value (' + str(meta) + ') has to be of type: ' + str(self.base_type))
            return Commands.Remove
        else:
            return False


class AllDiff(BoolOperator):
    def __init__(self, arg):
        self.arg = arg

    def evaluate(self, meta_list, params, default=None, line=None):
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

    def evaluate(self, meta, params, warning_only=False, default=None, line=None):
        props = []
        for v in self.values:
            prop = False
            if isinstance(v, BoolOperator) and not v.evaluate(meta, params, default, line):
                return False
            elif isinstance(v, MetaObject):
                prop = v.evaluate(meta, params, default, line)
            elif v == meta:
                prop = Atomic(v)
                prop.value = v
            if prop:
                if isinstance(prop, list):
                    props += prop
                else:
                    props.append(prop)

        if not props and warning_only:
            logger.warning(line, 'Value (' + str(meta) + ') is not allowed')
            if default:
                props = [default]
            else:
                props = [Commands.Remove]

        # two types of or: on a list or a value
        if not isinstance(meta, list) and len(props) == 1:
            return props[0]
        return props


class And(Operator):
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta, params, default=None, line=None):
        props = []
        for v in self.values:
            if isinstance(v, BoolOperator):
                if not v.evaluate(meta, params, default, line):
                    return False
            else:
                prop = v.evaluate(meta, params, default, line)
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
    def __init__(self, typ, warning_only=False):
        self.typ = typ
        self.warning_only = warning_only

    def evaluate(self, meta_list, params, default=None, line=None):
        props = []
        warn = []
        for meta in meta_list:
            prop = self.typ.evaluate(meta, params, default, line)
            if not prop:
                if self.warning_only:
                    warn.append(str(meta))
                else:
                    return False
            else:
                if isinstance(prop, list):
                    props += prop
                else:
                    props.append(prop)

        if props and warn:
            logger.warning(line, 'Any items that are not valid objects '
                                 'of the type expected are ignored: ' + str(warn))
        return props


class Some(Operator):
    """
    Some operator
    Takes a Type in constructor.
    On evaluation, checks if some of given items have the given type.
    """
    def __init__(self, typ):
        self.typ = typ

    def evaluate(self, meta_list, params, default=None, line=None):
        props = []
        valid = False
        for meta in meta_list:
            prop = self.typ.evaluate(meta, params, default, line)
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

    def evaluate(self, meta, params, default=None, line=None):
        prop = False
        for v in self.values:
            tmp = v.evaluate(meta, params, default, line)
            if tmp and prop:
                # already the second match
                logger.debug(line, '(Selection Operator) Only one match allowed: ' + str(meta))
                return False
            if tmp:
                prop = tmp
        # if we get here, we found zero or one match
        return prop

class SetOrDefault(Operator):
    """
    Used for tableDirection. If the given value is not in a predefined set than the default value is used.
    If no default value is provided for that property, it generates a warning
    and behave as if the property had not been specified.
    """
    def __init__(self, *values):
        self.values = list(values)

    def evaluate(self, meta, params, default=None, line=None):
        prop = 'not given'
        for v in self.values:
            if v == meta:
                prop = meta
                break
        if prop == 'not given':
            if default:
                prop = default
            else:
                logger.warning(line, 'Unknown value (no default value is provided for that property): ' + str(meta))
                prop = Commands.Remove
        return prop

FORMAT = {
    'decimalChar': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': '.'
    },
    'groupChar': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': ','
    },
    'pattern': {
        'options': [],
        'type': Atomic(OfType(basestring))
    },
}

DATATYPE = {
    'base': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': 'string'
    },
    'format': {
        # TODO object property
        'options': [],
        'type': Atomic(Or(OfType(basestring), Object(FORMAT)))
    },
    'length': {
        'options': [],
        'type': Atomic(OfType(int))
    },
    'minLength': {
        'options': [],
        'type': Atomic(OfType(int))
    }
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
        'type': Atomic(OfType(basestring, warning_only=True)),
        'default': ''
    },
    'lang': {
        'options': [],
        'type': Atomic(OfType(basestring)),
        'default': 'und'
    },
    'null': {
        'options': [],
        'type': Atomic(OfType(basestring, warning_only=True)),
        'default': ''
    },
    'ordered': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
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
        'type': Atomic(OfType(basestring, warning_only=True)),
        'default': None
    },
    'textDirection': {
        'options': [],
        'type': Atomic(SetOrDefault('ltr', 'rtl')),
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
        'type': Atomic(OfType(basestring, warning_only=True))
    },
    'suppressOutput': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
        'default': False
    },
    'titles': {
        'options': [],
        'type': NaturalLanguage()
    },
    'virtual': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
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
        'type': Array(And(All(Object(COLUMN, inherited_obj=INHERITED, common_properties=True), warning_only=True),
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
        'type': Atomic(OfType(list, warning_only=True)),
        'default': ["\r\n", "\n"]
    },
    'quoteChar': {
        'options': [],
        'type': Atomic(Or(OfType(basestring), None)),
        'default': '"'
    },
    'doubleQuote': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
        'default': True
    },
    'skipRows': {
        'options': [],
        'type': Atomic(OfType(int, warning_only=True)),
        'default': 0
    },
    'commentPrefix': {
        'options': [],
        'type': Atomic(OfType(basestring, warning_only=True)),
        'default': '#'
    },
    'header': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
        'default': True
    },
    'headerRowCount': {
        'options': [],
        'type': Atomic(OfType(int, warning_only=True)),
        'default': 1
    },
    'delimiter': {
        'options': [],
        'type': Atomic(OfType(basestring, warning_only=True)),
        'default': ','
    },
    'skipColumns': {
        'options': [],
        'type': Atomic(OfType(int, warning_only=True)),
        'default': 0
    },
    'skipBlankRows': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
        'default': False
    },
    'skipInitialSpace': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
        'default': False
    },
    'trim': {
        'options': [],
        'type': Atomic(SetOrDefault(True, False, 'start', 'end')),
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
    'url': {
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
        'type': Array(All(Object(TRANSFORMATION), warning_only=True), warning_only=True)
    },
    'tableDirection': {
        'options': [],
        'type': Atomic(SetOrDefault('rtl', 'ltr', 'default')),
        'default': 'default'
    },
    'tableSchema': {
        'options': [],
        'type': Object(SCHEMA, inherited_obj=INHERITED, common_properties=True)
    },
    'dialect': {
        'options': [],
        'type': Object(DIALECT, warning_only=True)
    },
    'notes': {
        'options': [],
        'type': Array(All(Object({}, common_properties=True)))
    },
    'suppressOutput': {
        'options': [],
        'type': Atomic(OfType(bool, warning_only=True)),
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
        'type': Array(All(Object(TABLE, inherited_obj=INHERITED, common_properties=True), warning_only=True))
    },
    'transformations': {
        'options': [],
        'type': Array(All(Object(TRANSFORMATION)))
    },
    'tableDirection': {
        'options': [],
        'type': Atomic(SetOrDefault('rtl', 'ltr', 'default')),
        'default': 'default'
    },
    'tableSchema': {
        'options': [],
        'type': Object(SCHEMA, inherited_obj=INHERITED, common_properties=True)
    },
    'dialect': {
        'options': [],
        'type': Object(DIALECT, warning_only=True)
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


def _validate(line, meta, params, schema, common_properties):
    model = {}
    remove_props = []
    default = None
    for prop in meta:
        value = meta[prop]
        if prop in schema:
            opts = schema[prop]['options']
            t = schema[prop]['type']
            # check for default value
            if 'default' in schema[prop]:
                default = schema[prop]['default']
            # check if not empty
            if value:
                prop_eval = t.evaluate(value, params, default, line)
                if prop_eval == Commands.Remove:
                    remove_props.append(prop)
                elif not prop_eval:
                    return False
                model[prop] = prop_eval
            elif Option.NonEmpty in opts:
                logger.debug(line, 'Property is empty: ' + str(prop))
                if prop == 'tables':
                    logger.error(line, 'array does not contain one or more "table descriptions"')
                return False
        elif common_properties and is_common_property(prop):
            prop_eval = Common(prop).evaluate(value, params, default, line)
            if not prop_eval:
                return False
            model[prop] = prop_eval
        else:
            logger.warning(line, 'Unknown property: ' + str(prop))
            model[prop] = Atomic(prop)
    # check for missing props
    for prop in schema:
        if Option.Required in schema[prop]['options'] and prop not in meta:
            logger.error(line, 'Property missing: ' + str(prop))
            return False
    # remove props with warnings
    for prop in remove_props:
        del model[prop]
    return model


def validate(metadata):
    metadata = expand(metadata)
    # outer_group = Or(Object(TABLE_GROUP, inherited_obj=INHERITED, common_properties=True), Object(TABLE, inherited_obj=INHERITED, common_properties=True))
    outer_group = Object(TABLE_GROUP, inherited_obj=INHERITED, common_properties=True)
    params = {}
    validated = outer_group.evaluate(metadata, params)
    # TODO look for language, column references, ...
    if validated:
        return Model(validated, params)
    return False


def expand(meta):
    # turn into table group description
    if 'tables' not in meta:
        tmp = {'tables': [meta]}
        context = meta.pop('@context', None)
        if context:
            tmp['@context'] = context
        return tmp
    return meta


class Model:
    def __init__(self, obj, params):
        self.params = params
        self.object = obj

    def normalize(self):
        self.object.normalize(self.params)

    def merge(self, B):
        self.object.merge(B.object)

    def json(self):
        return self.object.json()


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
    model = validate(metadata)
    if model:
        model.normalize()
    return model


def merge(meta_sources):
    """
    from highest priority to lowest priority by merging the first two metadata files
    """
    # at first normalize (and validate) the metadata objects
    norm_sources = []
    for s in meta_sources:
        norm = normalize(s)
        if norm:
            norm_sources.append(norm)
        else:
            raise ValidationException('validation failed for metadata: ' + str(s))


    # then merge them into one object
    A = None
    for m in norm_sources:
        # check if m is a valid metadata object
        if m:
            B = m
            # check if we are in the first iteration
            if not A:
                A = B
            else:
                A.merge(B)
    return A


