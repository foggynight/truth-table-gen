# truth-table-gen.py - Generate a truth table from a boolean expression.
# Copyright (C) 2026 Robert Coffey
# Released under the MIT license.

def error(msg):
    raise Exception(f'error: {msg}')

# parser -----------------------------------------------------------------------
#
# TODO: | Add prime for invert. e.g. X' = not X
# Grammar:
#   EXPR -> TERM ("+" EXPR)?
#   TERM -> PROD ("*" TERM)?
#         | PROD (TERM)?
#   PROD -> VAR
#         | "(" EXPR ")"
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
    if next() == '(':
        consume()
        expr = parse_expr()
        expect(')')
        return expr
    else:
        return parse_var()

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
    else:             return ('*', left, right)

def parse_expr():
    left = parse_term()
    if next() == '+':
        consume()
        right = parse_expr()
        return ('+', left, right)
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
    try:
        expr = parse(string)
        print(expr)
    except Exception as e:
        print(str(e))
