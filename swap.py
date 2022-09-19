import sys
import inspect


# shamelessly stolen from https://github.com/dankeyy/arg_repr.py
# embedding arg_repr here is simpler than importing it
# so-


def _parens(code):
    opening = closing = 0
    marks = []

    for i, v in enumerate(code):

        if code[i-1] != '\\' or code[i-2:i] == "\\\\":

            if v in ("'", '"'):
                marks.append(v)

            elif marks and marks[-1] == v:
                marks.pop()

                if not marks:
                    return i

        if len(marks) != 1:
            if   v == '(': opening += 1
            elif v == ')': closing += 1

        if closing > opening:
            return i


def _myargs_repr():
    func_name = inspect.stack()[1][3]
    parent_frame = inspect.stack()[2][0]
    lineo = parent_frame.f_lineno-1
    upper_frame = parent_frame
    while upper_frame.f_back:
        upper_frame = upper_frame.f_back

    code = inspect.getsource(upper_frame)

    # seek beginning of function call by traversing the code until call line
    line = p = 0
    while line != lineo:
        if code[p] == '\n':
            line += 1
        p += 1

    # slice the code
    # from beginning of call (after opening paren)
    # up until the last relevant closing paren
    code = code[p:]
    code = code[code.index(func_name) + len(func_name) + 1:]
    code = code[:_parens(code)] # _parens might return None but that's ok, [:None] is valid

    # code is now a repr of the function call arguments
    return code

# -------------------------------------------------------------------------------------

def swap(*args):
    if len(args) != 2:
        raise ValueError("Must supply exactly 2 arguments")

    parent_frame = sys._getframe().f_back
    parent_locals = parent_frame.f_locals

    outer_bindings = _myargs_repr().partition(',')
    a,_, b = map(str.strip, outer_bindings)

    parent_a = parent_locals.get(a)
    parent_b = parent_locals.get(b)

    if None in (parent_a, parent_b):
        raise ValueError("Bad arguments to swap")

    parent_locals[a], parent_locals[b] = parent_b, parent_a
