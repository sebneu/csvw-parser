__author__ = 'sebastian'


def validate(metadata):
    # TODO
    return metadata


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
