"""
Parse (our subset of) Linogram source code.

The grammar is a direct port of the one in Higher Order Perl,
which is copyright by Mark Jason Dominus.
"""

from parson import Grammar
from structs import Struct

Definition   = Struct('Definition', 'id extends decls')
TypeDecl     = Struct('TypeDecl', 'id decls')
Declarator   = Struct('Declarator', 'id params')
Constraints  = Struct('Constraints', 'equations')

Draw         = Struct('Draw', 'drawables')
DrawFunction = Struct('DrawFunction', 'fn_name')
DrawName     = Struct('DrawName', 'name')

Add    = Struct('+', 'arg1 arg2')
Sub    = Struct('-', 'arg1 arg2')
Mul    = Struct('*', 'arg1 arg2')
Div    = Struct('/', 'arg1 arg2')
Negate = lambda expr: Sub(Number(0), expr)

Tuple  = Struct('Tuple', 'exprs')

Name   = Struct('Name', 'id')
Dot    = Struct('Dot', 'base field')

Number = Struct('Number', 'value')

def maybe(*args):
    assert len(args) <= 1
    return args[0] if args else None

grammar = Grammar(r"""
program: _ (definition | declaration)* !/./.

definition: defheader '{'_ [declaration* :hug] '}'_   :Definition.
defheader: 'define'__ ID [('extends'__ ID)? :maybe].

declaration: type declarators ';'_   :TypeDecl
           | constraint_section
           | draw_section.
declarators: declarator (','_ declarator)*   :hug.

type: ID.

declarator: ID [('('_ params ')'_)? :maybe]   :Declarator.
params = param_spec (','_ param_spec)*.
param_spec: ID '='_ expression.

constraint_section: 'constraints'__ '{'_ constraint* '}'_   :hug :Constraints.
constraint: expression '='_ expression ';'_.

draw_section: 'draw'__ '{'_ drawable* '}'_   :hug :Draw.
drawable: name ';'_      :DrawName
        | '&'_ ID ';'_   :DrawFunction.

expression: term ('+'_ term :Add
                 |'-'_ term :Sub)*.
term:       atom ('*'_ atom :Mul
                 |'/'_ atom :Div)*.

atom: name
    | tuple
    | NUMBER            :Number
    | '-'_ expression   :Negate
    | '('_ expression ')'_.

name: ID :Name ('.'_ ID :Dot)*.

tuple: '('_ expression (','_ expression)+ ')'_   :hug :Tuple.


# Lexical grammar

NUMBER:    { mantissa /[eE]\d+/? } _  :float.
mantissa = /\d+/ ('.' /\d*/)?
         | '.' /\d+/.

ID       = /([a-zA-Z_]\w*)/ _.   # XXX need to rule out keywords?

__       = /\b/_.   # (i.e. a keyword must match up to a word boundary)

_        = /\s*/.
""")
parser = grammar(**globals())
