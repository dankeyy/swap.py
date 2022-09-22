import os
import sys
import inspect
from ctypes import pythonapi, py_object


# slightly adjusted version of https://github.com/dankeyy/arg_repr.py

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
    func_name = "swap"
    upper_frame = sys._getframe(2)

    #        line called              first line in frame that called
    lineo = upper_frame.f_lineno - upper_frame.f_code.co_firstlineno
    code = inspect.getsource(upper_frame)

    # seek beginning of call line by traversing the code until the lineo-th newline
    line = p = 0
    while line != lineo:
        if code[p] == os.linesep:
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
    """swaps two variables in-place, raises ValueError for invalid arguments such as literals"""

    if len(args) != 2:
        raise ValueError("Supply exactly 2 arguments")

    parent_frame = sys._getframe(1)
    parent_locals = parent_frame.f_locals

    # parse and clean args
    outer_bindings = _myargs_repr().partition(',')
    a, _, b = map(str.strip, outer_bindings)

    parent_a = parent_locals.get(a)
    parent_b = parent_locals.get(b)

    # if it wasn't found (dict.get returned None) something doesn't is weird
    # because allegedly it was called this way (found by arg_repr) so it should be in f_locals.
    # so that maybe user tried to pass something dumb like numbers/ string literals /complex data structures
    # instead of bindings. in any of these cases, raise ValueError
    if None in (parent_a, parent_b):
        raise ValueError("Bad arguments to swap")

    # swap
    parent_locals[a], parent_locals[b] = parent_b, parent_a

    # write changes to frame's fastlocals so it persists
    pythonapi.PyFrame_LocalsToFast.argtypes = [py_object]
    pythonapi.PyFrame_LocalsToFast(parent_frame)
