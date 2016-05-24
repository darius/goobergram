"""
Abstract syntax
"""

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
