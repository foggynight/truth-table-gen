# truth-table-gen.py - Generate a truth table from a boolean expression.
# Copyright (C) 2026 Robert Coffey
# Released under the MIT license.

from enum import Enum, auto
from sys import argv

def error(msg):
    raise Exception(f'error: {msg}')

def list_print(it):
    for e in it:
        print(e)

# expr (AST) -------------------------------------------------------------------
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

# Get a list of the variables in an expression.
def expr_vars(expr):
    vars = []
    def walk(e):
        if type(e) == str:
            vars.append(e)
        elif type(expr) != tuple:
            error('invalid expr, not string or tuple')
        else:
            for x in e[1:]:
                walk(x)
    walk(expr)
    return vars

# Generate all combinations of bindings given a list of variables.
def var_bind_combos(vars):
    pairs = [[v, False] for v in vars]
    pairs.reverse()

    def pairs_increment():
        for i in range(len(pairs)):
            pairs[i][1] = not pairs[i][1]
            carry = pairs[i][1] == False
            if carry == False:
                break

    combos = [dict(reversed(pairs))]
    for i in range(2**len(vars) - 1):
        pairs_increment()
        combos.append(dict(reversed(pairs)))
    return combos

# Evaluate an expression given a set of variable bindings.
def expr_eval(expr, binds: dict[chr, bool]):
    if type(expr) == str:
        return binds[expr]
    elif type(expr) != tuple:
        error('invalid expr, not string or tuple')

    match expr[0]:
        case Op.NOT:
            return not eval_expr(expr[1], binds)
        case Op.AND:
            return eval_expr(expr[1], binds) and eval_expr(expr[2], binds)
        case Op.OR:
            return eval_expr(expr[1], binds) or eval_expr(expr[2], binds)
        case _:
            error(f'unknown op: {expr[0]}')

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

# printer ----------------------------------------------------------------------

def print_tt_header(vars):
    pass

def print_tt_row(binds):
    pass

def print_truth_table(vars, binds_list):
    print_tt_header(vars)
    for binds in binds_list:
        print_tt_row(binds)

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
    print(expr_eval(expr, binds))

if __name__ == '__main__':
    main(argv[1])
