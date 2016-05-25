"""
Abstract syntax and its interpreter.
"""

from structs import Struct
import linear_constraints as LC

def run(program):
    env = {'number': NumberType()}
    type_ = Type(Definition('<program>', None, program),
                 env)
    inst = type_.instantiate(env, ())
    for part in inst.get_parts():
        part.draw()


class NumberType(object):
    def instantiate(self, env, params):
        assert not params
        return LC.Number()      # TODO give it a name and a type?
    def draw(self, inst):       # XXX never called because LC.Number doesn't point back to the type
        pass

class Type(Struct('defn env')):
    def instantiate(self, env, params):
        inst = Instance(self) # XXX use self.defn.extends if present
        self.defn.populate(inst, env)
        for id, expr in params:
            assert False, 'XXX'
        return inst
    def draw(self, inst):
        self.defn.draw(inst, self.env)
    def __repr__(self):
        return '<type %s>' % self.defn.id

class Instance(LC.Compound):
    def __init__(self, type_):
        LC.Compound.__init__(self, {})
        self.type = type_
    def draw(self):
        self.type.draw(self)
    def __repr__(self):
        return '<instance of %r: %r>' % (self.type, sorted(self.keys()))


class Definition(Struct('id extends decls')):
    def build(self, inst, env):
        env[self.id] = Type(self, env)
    def populate(self, inst, env):
        for decl in self.decls:
            decl.build(inst, env)
    def draw(self, inst, env):
        for decl in self.decls:
            decl.draw(inst, env)

class VarDecl(Struct('type_id decls')):
    def build(self, inst, env):
        type_ = env[self.type_id]
        assert isinstance(type_, (Type, NumberType)), "%r is not a type" % type_
        for decl in self.decls:
            inst.mapping[decl.id] = type_.instantiate(env, decl.params)
    def draw(self, inst, env):
        pass

Declarator = Struct('id params', name='Declarator')

class Constraints(Struct('equations')):
    def build(self, inst, env):
        for lhs, rhs in self.equations:
            LC.equate(lhs.evaluate(inst, env), rhs.evaluate(inst, env))
    def draw(self, inst, env):
        pass

class Draw(Struct('drawables')):
    def build(self, inst, env):
        pass
    def draw(self, inst, env):
        for drawable in self.drawables:
            drawable.draw(inst, env)

class DrawFunction(Struct('fn_name')):
    def draw(self, inst, env):
        draw_functions[self.fn_name](**inst.mapping)

class DrawName(Struct('name')):
    def draw(self, inst, env):
        self.name.evaluate(inst, env).draw()

class Add(Struct('arg1 arg2')):
    def evaluate(self, inst, env):
        return self.arg1.evaluate(inst, env) + self.arg2.evaluate(inst, env)

class Sub(Struct('arg1 arg2')):
    def evaluate(self, inst, env):
        return self.arg1.evaluate(inst, env) - self.arg2.evaluate(inst, env)

class Mul(Struct('arg1 arg2')):
    def evaluate(self, inst, env):
        return self.arg1.evaluate(inst, env) * self.arg2.evaluate(inst, env)

class Div(Struct('arg1 arg2')):
    def evaluate(self, inst, env):
        return self.arg1.evaluate(inst, env) / self.arg2.evaluate(inst, env)

Negate = lambda expr: Sub(Number(0), expr)

class Tuple(Struct('exprs')):
    def evaluate(self, inst, env):
        assert len(self.exprs) in tuple_types
        params = zip('xyz', self.exprs)
        return tuple_types[len(self.exprs)].instantiate(env, params)

class Name(Struct('id')):
    def evaluate(self, inst, env):
        if self.id not in inst.mapping:
            assert 0, "not found: %r in %r" % (self.id, inst)
        return inst.mapping[self.id] # XXX what about env?

class Dot(Struct('base field')):
    def evaluate(self, inst, env):
        return self.base.evaluate(inst, env).mapping[self.field]

class Number(Struct('value')):
    def evaluate(self, inst, env):
        return self.value

tuple_types = {} # XXX

def draw_foo(a, b):          # XXX just for the smoke test
    print 'draw foo', a.get_value(), b.get_value()

def draw_point(x, y):          # XXX just for the smoke test
    print 'draw point', x.get_value(), y.get_value()

draw_functions = dict(draw_foo=draw_foo,
                      draw_point=draw_point)
