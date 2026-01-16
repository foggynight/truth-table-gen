# truth-table-gen.py - Generate a truth table from a boolean expression.
# Copyright (C) 2026 Robert Coffey
# Released under the MIT license.

from enum import Enum, auto
from sys import argv

def error(msg):
    raise Exception(f'error: {msg}')

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
    vars = set()
    def walk(e):
        if type(e) == str:
            vars.add(e)
        elif type(expr) != tuple:
            error('invalid expr, not string or tuple')
        else:
            for x in e[1:]:
                walk(x)
    walk(expr)
    return sorted(list(vars))

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
            return not expr_eval(expr[1], binds)
        case Op.AND:
            return expr_eval(expr[1], binds) and expr_eval(expr[2], binds)
        case Op.OR:
            return expr_eval(expr[1], binds) or expr_eval(expr[2], binds)
        case _:
            error(f'unknown op: {expr[0]}')

# parser -----------------------------------------------------------------------
# Recursive descent expression parser.
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

# Parse a single expression contained in `string`.
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

def print_tt_header(vars, output_var=' '):
    print('|', end='')
    for v in vars:
        print(f' {v}', end='')
    print(f' | {output_var} |')
    cross_bar = '-' * (1 + 2*len(vars) + 6)
    print(cross_bar)

def print_tt_row(input_vals: [bool], output_val: bool):
    print('|', end='')
    for v in input_vals:
        print(f' {v}', end='')
    print(f' | {output_val} |')

# main -------------------------------------------------------------------------

def gen_truth_table(expr):
    vars = expr_vars(expr)
    bind_combos = var_bind_combos(vars)
    print_tt_header(vars)
    for binds in bind_combos:
        vals = [1 if binds[var] else 0 for var in vars]
        result = 1 if expr_eval(expr, binds) else 0
        print_tt_row(vals, result)

def main(string: str):
    expr = None
    try:
        expr = parse(string)
    except Exception as e:
        print(str(e))
        return
    gen_truth_table(expr)

if __name__ == '__main__':
    main(argv[1])
