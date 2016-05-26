"""
Parse Linogram source code as defined in HOP.
(The full Perl Linogram has more features.)

The grammar is a direct port of the one in Higher Order Perl,
which is copyright by Mark Jason Dominus.
"""

from parson import Grammar
import absyntax

grammar = Grammar(r"""
program: _ (definition | declaration)* ('__END__' | !/./).

definition: defheader '{'_ [declaration* :hug] '}'_   :Definition.
defheader: 'define'__ ID ['extends'__ ID | :None].

declaration: ID declarators ';'_   :VarDecl
           | constraint_section
           | draw_section.

declarators: declarator (','_ declarator)*   :hug.
declarator: ID [('('_ params ')'_)? :hug]   :Declarator.
params = param_spec (','_ param_spec)*.
param_spec: ID '='_ expression   :hug.

constraint_section: 'constraints'__ '{'_ constraint* '}'_   :hug :Constraints.
constraint: expression '='_ expression ';'_ :hug.

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
parser = grammar(**absyntax.__dict__)
