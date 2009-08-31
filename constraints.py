class Variable:
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
#        print 'solve', self.constraints
        assert self.constraints
        list(self.constraints)[0].solve()
    def add_connected_constraints(self, constraints):
        for constraint in self.constraints:
            constraint.add_connected_constraints(constraints)
    def assign(self, value):
        assert self.value is None or self.value == value
        self.value = value

class Constraint:
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
