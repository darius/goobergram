"""
A variable may have a value; a constraint enforces a relation
between variables. Variables and constraints form a network.
"""

class Variable(object):
    def __init__(self):
        self.constraints = set()
        self.value = None
    def constrain(self, constraint):
        if self.value is None:
            self.constraints.add(constraint)
    def get_value(self):
        if self.value is None: self.solve()
        return self.value
    def solve(self):
        assert self.constraints, "Unconstrained: %r" % self
        next(iter(self.constraints)).solve() # XXX solve them all?
    def add_connected_constraints(self, constraints):
        for constraint in self.constraints:
            constraint.add_connected_constraints(constraints)
    def assign(self, value):
        assert self.value is None or self.value == value
        self.value = value

class Constraint(object):
    def solve(self):
        abstract
    def get_variables(self):
        abstract
    def get_connected_constraints(self):
        constraints = set()
        self.add_connected_constraints(constraints)
        return constraints
    def add_connected_constraints(self, constraints):
        if self in constraints: return
        constraints.add(self)
        for variable in self.get_variables():
            variable.add_connected_constraints(constraints)
