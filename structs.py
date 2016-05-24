"""
Define a named-tuple-like type, but simpler.
"""

# TODO figure out how to use __slots__

def Struct(my_name, field_names, supertype=(object,)):
    if isinstance(field_names, (str, unicode)):
        field_names = tuple(field_names.split())

    def __init__(self, *args):
        if len(field_names) != len(args):
	    raise TypeError("%s takes %d arguments (%d given)"
                            % (my_name, len(field_names), len(args)))
        self.__dict__.update(zip(field_names, args))

    def __repr__(self):
        return '%s(%s)' % (my_name, ', '.join(repr(getattr(self, f))
                                              for f in field_names))

    # (for use with pprint)
    def my_as_sexpr(self):         # XXX better name?
        return (my_name,) + tuple(as_sexpr(getattr(self, f))
                                  for f in field_names)
    my_as_sexpr.__name__ = 'as_sexpr'

    return type(my_name,
                supertype,
                dict(__init__=__init__,
                     __repr__=__repr__,
                     as_sexpr=my_as_sexpr))

def as_sexpr(obj):
    if hasattr(obj, 'as_sexpr'):
        return getattr(obj, 'as_sexpr')()
    elif isinstance(obj, list):
        return map(as_sexpr, obj)
    elif isinstance(obj, tuple):
        return tuple(map(as_sexpr, obj))
    else:
        return obj
