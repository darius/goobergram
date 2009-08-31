"""
Trivial implementation of Boolean constraints. The main constraints
module is supposed to be usable for many kinds of constraint networks,
not just the linear equations used by linogram -- so let's try out
defining another kind.
XXX untested
"""

from constraints import *

class BC(Constraint):
    def __init__(self, variables, values):
        # values is a collection of tuples, each with a boolean for
        # each variable, corresponding to the variables in sorted
        # order.
        self.variables = frozenset(variables)
        self.values = frozenset(values)
    def solve(self):
        for variable, value in solve(self.connected_constraints()):
            variable.assign(value)
    def get_variables(self):
        return self.variables
    def allows(self, asgn):
        t = tuple(val for v, val in asgn if v in self.variables)
        return t in self.values

def solve(bcs):
    vars = set()
    for bc in bcs:
        vars |= set(bc.variables)
    for asgn in assignments(sorted(vars)):
        for bc in bcs:
            if not bc.allows(asgn):
                continue
        return asgn.items()
    return ()

def assignments(vars):
    if not vars:
        yield ()
    else:
        v = vars[0]
        for asgn in assignments(vars[1:]):
            yield ((v, False),) + asgn
            yield ((v, True),) + asgn
