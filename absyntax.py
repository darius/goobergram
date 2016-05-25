"""
Abstract syntax and its interpreter.
"""

import operator

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
        return NumberInstance()

class NumberInstance(LC.Number):
    def draw(self):
        pass

class Type(Struct('defn env')):
    def instantiate(self, env, params):
        inst = Instance(self)
        self.defn.populate(inst, env)
        for id, expr in params:
            assert False, 'XXX'
        return inst
    def draw(self, inst):
        self.defn.draw(inst, self.env)
    def __repr__(self):
        return '<type %s>' % self.defn.id

class TupleType(Struct('fields')):
    def instantiate(self, env, params):
        inst = Instance(self)
        for f in self.fields:
            inst.mapping[f] = NumberInstance()
        for f, expr in params:
            LC.equate(inst.mapping[f], expr.evaluate(None, # XXX
                                                     env))
        return inst
    def draw(self, inst):
        pass
    def __repr__(self):
        return '<tuple-type %s>' % ','.join(self.fields)

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
        supe = self.super_definition(env)
        if supe:
            supe.populate(inst, env)  # XXX right env?
        for decl in self.decls:
            decl.build(inst, env)
    def draw(self, inst, env):
        supe = self.super_definition(env)
        if supe:
            supe.draw(inst, env) # XXX does the user always want this?
        for decl in self.decls:
            decl.draw(inst, env)
    def super_definition(self, env): # XXX use env from defn time, I guess
        if self.extends:
            supertype = env[self.extends]
            assert isinstance(supertype, Type), "%r is not a type" % supertype
            return supertype.defn
        else:
            return None

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


class BinaryOp(Struct('arg1 arg2')):
    def evaluate(self, inst, env):
        return self.operate(self.arg1.evaluate(inst, env),
                            self.arg2.evaluate(inst, env))

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

tuple_types = {
    2: TupleType('xy'),
}

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
