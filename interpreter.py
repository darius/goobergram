"""
Abstract syntax and its interpreter.
"""

import operator

from structs import Struct
import linear_constraints as LC

def run(program):
    types = {'number': NumberType()}
    env = Environment(types, None)
    main = Definition('<program>', None, program)
    inst = main.instantiate(env)
    inst.draw(env)


class Environment(Struct('types inst')):
    def spawn(self, inst):
        return Environment(self.types, inst)
    def init(self, id, value):
        assert id not in self.inst.mapping, "Multiple def: %s" % id
        self.inst.mapping[id] = value
    def fetch(self, id):
        assert id in self.inst.mapping, \
            "Not found: %r in %r" % (id, self.inst)
        return self.inst.mapping[id]

class NumberType(object):
    def instantiate(self, env):
        return NumberInstance()

class NumberInstance(LC.Number):
    def draw(self, env):
        pass

class Instance(LC.Compound):
    def __init__(self, type_):
        LC.Compound.__init__(self, {})
        self.type = type_
    def draw(self, env):
        self.type.draw(env.spawn(self))
    def __repr__(self):
        return '<instance of %r: %r>' % (self.type, sorted(self.keys()))

class TupleType(Struct('fields')):
    def instantiate(self, env):
        inst = Instance(self)
        for f in self.fields:
            inst.mapping[f] = NumberInstance()
        return inst
    def draw(self, env):
        pass

class Definition(Struct('id extends decls')):
    def build(self, env):
        env.types[self.id] = self
    def instantiate(self, env):
        inst = Instance(self)
        subenv = env.spawn(inst) # XXX won't see global vars; should it?
        self.populate(subenv)
        return inst
    def populate(self, env):
        supe = self.super_definition(env)
        if supe:
            supe.populate(env)
        for decl in self.decls:
            decl.build(env)
    def draw(self, env):
        for drawer in self.pick_drawers(env) or env.inst.get_parts():
            drawer.draw(env)
    def pick_drawers(self, env):
        defn = self
        while defn:
            decls = [decl for decl in defn.decls if isinstance(decl, Draw)]
            if decls: return decls
            defn = defn.super_definition(env)
        return []
    def super_definition(self, env):
        if self.extends:
            supertype = env.types[self.extends]
            assert isinstance(supertype, Definition), \
                "%r is not a definition" % supertype
            return supertype
        else:
            return None


class VarDecl(Struct('type_id decls')):
    def build(self, env):
        type_ = env.types[self.type_id]
        for decl in self.decls:
            inst = type_.instantiate(env)
            env.init(decl.id, inst)
            for id, expr in decl.params:
                LC.equate(inst.mapping[id], rhs.evaluate(env))
    def draw(self, env):
        pass

Declarator = Struct('id params', name='Declarator')


class Constraints(Struct('equations')):
    def build(self, env):
        for lhs, rhs in self.equations:
            LC.equate(lhs.evaluate(env), rhs.evaluate(env))
    def draw(self, env):
        pass


class Draw(Struct('drawables')):
    def build(self, env):
        pass
    def draw(self, env):
        for drawable in self.drawables:
            drawable.draw(env)

class DrawFunction(Struct('fn_name')):
    def draw(self, env):
        draw_functions[self.fn_name](**env.inst.mapping)

class DrawName(Struct('name')):
    def draw(self, env):
        self.name.evaluate(env).draw()


class BinaryOp(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.operate(self.arg1.evaluate(env),
                            self.arg2.evaluate(env))

class Add(BinaryOp): operate = operator.add
class Sub(BinaryOp): operate = operator.sub
class Mul(BinaryOp): operate = operator.mul
class Div(BinaryOp): operate = operator.div

def Negate(expr):
    return Sub(Number(0), expr)


class Tuple(Struct('exprs')):
    def evaluate(self, env):
        type_ = tuple_types[len(self.exprs)]
        inst = type_.instantiate(env)
        for v, expr in zip(type_.fields, self.exprs):
            LC.equate(inst.mapping[v], expr.evaluate(env))
        return inst

tuple_types = {
    2: TupleType('xy'),
}

class Name(Struct('id')):
    def evaluate(self, env):
        return env.fetch(self.id)

class Dot(Struct('base field')):
    def evaluate(self, env):
        return self.base.evaluate(env).mapping[self.field]

class Number(Struct('value')):
    def evaluate(self, env):
        return self.value

# XXX just for the smoke test:

def draw_foo(a, b):     
    print 'draw foo', a.get_value(), b.get_value()

def draw_point(x, y):
    print 'draw point', x.get_value(), y.get_value()

def draw_line(start, end, **kwargs):
    print 'draw line', ((start.x.get_value(), start.y.get_value()),
                        (end.x.get_value(),   end.y.get_value()))

draw_functions = dict(draw_foo=draw_foo,
                      draw_point=draw_point,
                      draw_line=draw_line,)
