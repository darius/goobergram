"""
Parse (our subset of) Linogram source code.
"""

from parson import Grammar

grammar = Grammar(r"""
program: _ (definition | declaration)* !/./.

definition: defheader '{'_ declaration* '}'_.
defheader: 'define'__ ID ('extends'__ ID)?.

declaration: type declarators ';'_
           | constraint_section
           | draw_section.
declarators: declarator (','_ declarator)*.

type: ID.

declarator: ID ('('_ params ')'_)?.
params = param_spec (','_ param_spec)*.
param_spec: ID '='_ expression.  # XXX name instead of ID?

constraint_section: 'constraints'__ '{'_ constraint* '}'_.
constraint: expression '='_ expression ';'_.

draw_section: 'draw'__ '{'_ drawable* '}'_.
drawable: name ';'_
        | '&'_ ID ';'_.

expression: term ('+'_ term
                 |'-'_ term)*.
term:       atom ('*'_ atom
                 |'/'_ atom)*.

atom: name
    | tuple
    | NUMBER
    | '-'_ expression
    | '('_ expression ')'_.

name: ID ('.'_ ID)*.

tuple: '('_ expression (','_ expression)+ ')'_.


# Lexical grammar

NUMBER:    { mantissa /[eE]\d+/? } _  :float.
mantissa = /\d+/ /[.]\d*/?
         | /[.]\d+/.

ID       = /([a-zA-Z_]\w*)/ _.   # XXX need to rule out keywords?

__       = /\b/_.   # (i.e. a keyword must match up to a word boundary)

_        = /\s*/.
""")
parser = grammar(**globals())
