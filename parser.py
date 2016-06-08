"""
Parse Linogram source code as defined in HOP.
(The full Perl Linogram has more features.)

The grammar is a direct port of the one in Higher Order Perl,
which is copyright by Mark Jason Dominus.
"""

from parson import Grammar, Unparsable
import interpreter

grammar = Grammar(r""" (definition | declaration)* ('__END__' | :end).

definition: defheader '{' [declaration* :hug] '}'   :Definition.
defheader: "define" ID ["extends" ID | :None].

declaration: ID declarators ';'   :VarDecl
           | constraint_section
           | draw_section.

declarators: declarator++','   :hug.
declarator: ID [('(' param_spec++',' ')')? :hug]   :Declarator.
param_spec: ID '=' expression   :hug.

constraint_section: "constraints" '{' constraint* '}'   :hug :Constraints.
constraint: expression '=' expression ';' :hug.

draw_section: "draw" '{' drawable* '}'   :hug :Draw.
drawable: name ';'     :DrawName
        | '&' ID ';'   :DrawFunction.

expression: term ('+' term :Add
                 |'-' term :Sub)*.
term:       atom ('*' atom :Mul
                 |'/' atom :Div)*.

atom: name
    | tuple
    | NUMBER           :Number
    | '-' expression   :Negate
    | '(' expression ')'.

name: ID :Name ('.' ID :Dot)*.

tuple: '(' expression (',' expression)+ ')'   :hug :Tuple.


# Lexical grammar

ID:          /([a-zA-Z_]\w*)/.   # XXX need to rule out keywords?

NUMBER   ~:  { mantissa /[eE]\d+/? } FNORD  :float.
mantissa ~:  /\d+/ ('.' /\d*/)?
           | '.' /\d+/.

FNORD    ~:  /\s*/.
""")
parse = grammar.bind(interpreter)
