"""
Abstract syntax
"""

from structs import Struct

def run(program):
    env = {}
    for stmt in program:
        stmt.build(env)
    print env.keys()

isa = isinstance

class Definition(Struct('id extends decls')):
    def build(self, env):
        env[self.id] = self     # XXX remember env too?
    def instantiate(self, env, params):
        return Instance(self, env)  # XXX

class Instance(Struct('defn env')):
    pass

class VarDecl(Struct('type_id decls')):
    def build(self, env):
        defn = env[self.type_id]
        assert isa(defn, Definition)
        for decl in self.decls:
            env[decl.id] = defn.instantiate(env, decl.params)

Declarator = Struct('id params', name='Declarator')

class Constraints(Struct('equations')):
    def build(self, env):
        for lhs, rhs in self.equations:
            equate(lhs.evaluate(env), rhs.evaluate(env))

def equate(thing1, thing2):
    pass #XXX

class Draw(Struct('drawables')):
    def build(self, env):
        env.setdefault('#draw', []).extend(self.drawables)

class DrawFunction(Struct('fn_name')):
    def draw(self, env):
        print 'draw: call', self.fn_name, env.keys()

class DrawName(Struct('name')):
    def draw(self, env):
        env[self.name].draw(env) # XXX or something

class Add(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.arg1.evaluate(env) + self.arg2.evaluate(env)

class Sub(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.arg1.evaluate(env) - self.arg2.evaluate(env)

class Mul(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.arg1.evaluate(env) * self.arg2.evaluate(env)

class Div(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.arg1.evaluate(env) / self.arg2.evaluate(env)

Negate = lambda expr: Sub(Number(0), expr)

class Tuple(Struct('exprs')):
    def evaluate(self, env):
        params = ['XXX' for expr in self.exprs]
        return tuple_defns[len(self.exprs)].instantiate(env, params) # XXX

class Name(Struct('id')):
    def evaluate(self, env):
        return env[self.id]

class Dot(Struct('base field')):
    def evaluate(self, env):
        return self.base.evaluate(env)[self.field] # XXX or something

class Number(Struct('value')):
    def evaluate(self, env):
        return self.value
