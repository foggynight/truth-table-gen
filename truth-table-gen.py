# truth-table-gen.py - Generate a truth table from a boolean expression.
# Copyright (C) 2026 Robert Coffey
# Released under the MIT license.

from enum import Enum, auto
from sys import argv

def error(msg):
    raise Exception(f'error: {msg}')

# AST --------------------------------------------------------------------------
# Abstract syntax tree is represented by either a character or a tuple.
#   - Single character represents a variable.
#   - Tuple of 2 elements represents a unary expression: (Op, AST)
#   - Tuple of 3 elements represents a binary expression: (Op, L_AST, R_AST)

class Op(Enum):
    NOT = auto()
    AND = auto()
    OR = auto()

    def __repr__(self):
        return self.name

def eval_ast(ast, binds: dict[chr, bool]):
    if type(ast) == str:
        return binds[ast]
    elif type(ast) != tuple:
        error('invalid ast, not string or tuple')

    match ast[0]:
        case Op.NOT:
            return not eval_ast(ast[1], binds)
        case Op.AND:
            return eval_ast(ast[1], binds) and eval_ast(ast[2], binds)
        case Op.OR:
            return eval_ast(ast[1], binds) or eval_ast(ast[2], binds)
        case _:
            error(f'unknown op: {ast[0]}')

# parser -----------------------------------------------------------------------
# Expression Grammar:
#   EXPR -> TERM ("+" EXPR)?
#   TERM -> PROD ("*" TERM)?
#         | PROD (TERM)?
#   PROD -> VAR INV?
#         | "(" EXPR ")" INV?
#   VAR  -> [a-zA-Z]

toks = None
toks_i = 0

def next():
    global toks, toks_i
    return toks[toks_i] if toks_i < len(toks) else None

def consume():
    global toks_i
    toks_i += 1

def expect(c: chr or None):
    if c != next():
        error(f"expected {c}, got '{next()}'")
    consume()

def parse_var():
    if next() is None or not next().isalpha():
        error(f"expected variable, got '{next()}'")
    var = next()
    consume()
    return var

def parse_prod():
    expr = None
    if next() == '(':
        consume()
        expr = parse_expr()
        expect(')')
    else:
        expr = parse_var()

    if next() == "'":
        consume()
        expr = (Op.NOT, expr)

    return expr

def parse_term():
    left = parse_prod()
    right = None

    if next() is not None and\
            (next().isalpha() or next() == '('):
        right = parse_term()
    elif next() == '*':
        consume()
        right = parse_term()

    if right is None: return left
    else:             return (Op.AND, left, right)

def parse_expr():
    left = parse_term()
    if next() == '+':
        consume()
        right = parse_expr()
        return (Op.OR, left, right)
    else: return left

def parse(string: str):
    global toks, toks_i
    toks = list(filter(
        lambda s: s != '' and not s.isspace(),
        string))
    toks_i = 0
    expr = parse_expr()
    expect(None)
    return expr

# main -------------------------------------------------------------------------

def main(string: str):
    expr = None
    try:
        expr = parse(string)
        print(expr)
    except Exception as e:
        print(str(e))
        return

    binds = {
        'a': 0,
        'b': 1,
        'c': 1,
        'd': 0,
    }
    print(eval_expr(expr, binds))

if __name__ == '__main__':
    main(argv[1])
