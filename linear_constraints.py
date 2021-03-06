"""
A linear constraint requires a linear combination of variables to = 0.
We represent the constraint as a linear expression, with the '=0' implicit.

We support compound values, too: they have named fields, and they do
arithmetic by operating on corresponding field values recursively.  We
used to require them all to match; now like actual Linogram we make the
result have only the fields that both have. (HOP p. 525.)

Still missing: Linogram supports arithmetic between a 'feature' (our
Expression) and a tuple (an (x,y) or (x,y,z) Compound, effectively).
In Linogram this automatically maps down the structure of the feature
until it reaches fields named like .x or .y. (HOP p. 526) I could add
a Tuple class and handle it specially, but I think I've learned enough
that it won't teach me more.
"""

import constraints
import linear_equations

class Variable(constraints.Variable):
    def __str__(self):
        return '<Variable %x>' % id(self)

class Constraint(constraints.Constraint):
    def __init__(self, lin_exp):
        self.lin_exp = lin_exp
        for variable in lin_exp.variables():
            variable.constrain(self)
    def get_variables(self):
        return self.lin_exp.variables()
    def solve(self):
        eqns = [c.lin_exp for c in self.get_connected_constraints()]
        for variable, value in linear_equations.solve_equations(eqns).items():
            variable.assign(value)

def equate(expr1, expr2):
    zero(as_expression(expr1) - expr2)

def zero(value):
    as_expression(value).as_constraints()

def as_expression(value):
    if isinstance(value, (int, float)):
        return Number(linear_equations.LinExp(value, ()))
    assert isinstance(value, Expression)
    return value

def as_scalar(value):
    if isinstance(value, (int, float)):
        return value
    return value.as_scalar()

class Expression(object):
    def as_constraints(self):
        abstract
    def as_scalar(self):
        abstract
    def coerce(self, value):
        abstract
    def combine(self, c, e2, c2):
        abstract
    def scale(self, c):
        abstract
    def __xor__(self, other):
        "Constrain me to equal other. (A giant abuse of notation.)"
        other = as_expression(other)
        equate(self, other)
        return other
    def __neg__(self):         return self.scale(-1)
    def __add__(self, value):  return self.combine(1, self.coerce(value), 1)
    def __sub__(self, value):  return self.combine(1, self.coerce(value), -1)
    def __mul__(self, value):  return self.scale(as_scalar(value))
    def __div__(self, value):  return self.scale(1. / as_scalar(value))
    def __radd__(self, value): return self.coerce(value).combine(1, self, 1)
    def __rsub__(self, value): return self.coerce(value).combine(1, self, -1)
    def __rmul__(self, value): return self.scale(as_scalar(value))
    def __rdiv__(self, value): return self.coerce(value) / self

class Number(Expression):
    def __init__(self, lin_exp=None):
        if lin_exp is None:
            lin_exp = linear_equations.LinExp(0, [(Variable(), 1)])
        self.lin_exp = lin_exp
    def as_constraints(self):
        return [Constraint(self.lin_exp)]
    def as_scalar(self):
        assert self.lin_exp.is_constant()
        return self.lin_exp.constant
    def coerce(self, value):
        value = as_expression(value)
        assert isinstance(value, Number)
        return value
    def combine(self, c, e2, c2):
        return Number(self.lin_exp.combine(c, e2.lin_exp, c2))
    def scale(self, c):
        return Number(self.lin_exp.scale(c))
    def get_value(self):
        return self.lin_exp.defines_var()[0].get_value()
    def __str__(self):
        return '<Number %r>' % self.lin_exp

class Compound(Expression):
    def __init__(self, mapping):
        self.mapping = mapping
    def add_parts(self, dict):
        self.mapping.update(dict)
    def as_constraints(self):
        return flatten(e.as_constraints() for e in self.mapping.values())
    def as_scalar(self):
        assert False
    def coerce(self, value):
        if isinstance(value, Compound):
            mapping = value.mapping
        elif isinstance(value, dict):
            mapping = value
        else:
            assert False, "Not a Compound: %r" % (value,)
        return Compound({k: v for k,v in mapping.iteritems()
                         if k in self.mapping})
    def combine(self, c, e2, c2):
        return Compound({key: (c * self.mapping[key]
                               + c2 * e2.mapping[key])
                         for key in self.mapping.keys()})
    def scale(self, c):
        return Compound({key: c * self.mapping[key]
                         for key in self.mapping.keys()})
    def keys(self):
        return set(self.mapping.keys())
    def get_parts(self):
        return self.mapping.itervalues()
    def __getattr__(self, name):
        try:
            return self.mapping[name]
        except KeyError:
            raise AttributeError(name)
    def __str__(self):
        return '<Compound of %s>' % sorted(self.mapping.keys())

def flatten(lists):
    return sum(lists, [])
