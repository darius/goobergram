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
    inst = main.instantiate(env, ())
    for part in inst.get_parts():
        part.draw(env)


class Environment(Struct('types inst')):
    def spawn(self, inst):
        return Environment(self.types, inst)

class NumberType(object):
    def instantiate(self, env, params):
        assert not params
        return NumberInstance()

class NumberInstance(LC.Number):
    def draw(self, env):
        pass

class TupleType(Struct('fields')):
    def instantiate(self, env, params):
        inst = Instance(self)
        for f in self.fields:
            inst.mapping[f] = NumberInstance()
        subenv = env.spawn(inst)
        for f, expr in params:
            LC.equate(inst.mapping[f], expr.evaluate(subenv))
        return inst
    def draw(self, env):
        pass
    def __repr__(self):
        return '<tuple-type %s>' % ','.join(self.fields)

class Instance(LC.Compound):
    def __init__(self, type_):
        LC.Compound.__init__(self, {})
        self.type = type_
    def draw(self, env):
        self.type.draw(env.spawn(self))
    def __repr__(self):
        return '<instance of %r: %r>' % (self.type, sorted(self.keys()))


class Definition(Struct('id extends decls')):
    def build(self, env):
        env.types[self.id] = self
    def instantiate(self, env, params):
        inst = Instance(self)
        subenv = env.spawn(inst) # XXX won't see global vars
        self.populate(subenv)
        for id, expr in params:
            assert False, 'XXX'
        return inst
    def populate(self, env):
        supe = self.super_definition(env)
        if supe:
            supe.populate(env)
        for decl in self.decls:
            decl.build(env)
    def draw(self, env):
        supe = self.super_definition(env)
        if supe:
            supe.draw(env) # XXX does the user always want this?
        for decl in self.decls:
            decl.draw(env)
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
            env.inst.mapping[decl.id] = type_.instantiate(env, decl.params)
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

class Add(BinaryOp):
    operate = operator.add

class Sub(BinaryOp):
    operate = operator.sub

class Mul(BinaryOp):
    operate = operator.mul

class Div(BinaryOp):
    operate = operator.div

def Negate(expr):
    return Sub(Number(0), expr)


class Tuple(Struct('exprs')):
    def evaluate(self, env):
        assert len(self.exprs) in tuple_types
        params = zip('xyz', self.exprs)
        return tuple_types[len(self.exprs)].instantiate(env, params)

tuple_types = {
    2: TupleType('xy'),
}

class Name(Struct('id')):
    def evaluate(self, env):
        if self.id not in env.inst.mapping:
            assert 0, "not found: %r in %r" % (self.id, env.inst)
        return env.inst.mapping[self.id]

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
