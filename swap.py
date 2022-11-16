import os
import sys
import inspect
from ctypes import pythonapi, py_object

# utils for checking if running in interactive shell mode
# -------------------------------------------------------------------------------------

def _prompt():
    import readline
    i = readline.get_current_history_length()
    line = ''
    # for interactive mode, we're going to be lazy
    # and check only for single line calls
    # sorry
    while 'swap(' not in line:
        line = readline.get_history_item(i)
        i -= 1
    return line


def _in_ipython():
    try:
        return __IPYTHON__
    except NameError:
        return False


# parsing utilities
# -------------------------------------------------------------------------------------
def _parens(code):
    """Get index of closing paren"""
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



def _myargs_repr(in_interactive_shell, in_ipython):
    # adjusted version of https://github.com/dankeyy/arg_repr.py
    func_name = "swap"

    if in_interactive_shell and not in_ipython:
        code = _prompt()

    else: # in ipython/ file
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

    code = code[code.index(func_name + '(') + len(func_name) + 1:]
    code = code[:_parens(code)] # _parens might return None but that's ok, [:None] is valid

        # code is now a repr of the function call arguments
    return code

# -------------------------------------------------------------------------------------

def swap(*args):
    """swaps two variables in-place, raises ValueError for invalid arguments such as literals"""

    if len(args) != 2:
        raise ValueError("Supply exactly 2 arguments")

    ipython = _in_ipython()
    interactive_shell = hasattr(sys, 'ps1')

    parent_frame   = sys._getframe(1)
    parent_locals  = parent_frame.f_locals

    # parse and clean args
    outer_bindings = _myargs_repr(interactive_shell, ipython).partition(',')
    a, _, b = map(str.strip, outer_bindings)

    parent_a = parent_locals.get(a)
    parent_b = parent_locals.get(b)

    # maybe user tried to pass something dumb
    # instead of bindings. in any of these cases, raise ValueError
    if None in (parent_a, parent_b):
        # but... if input is in fact valid, and we still got here,
        # chances are the function is called from interactive mode
        # and trying to swap variables *from its own frame* with the actual call to swap *inside a function* (to which it calls),
        # (otherwise it would have been found in parent_locals)
        # in this case we could just check the upper frame

        if interactive_shell or ipython:
            parent_frame  = sys._getframe(2)
            # The following is 100% identical to the logic above,
            # and could probably be abstracted by an external function
            # with small adjustments to match upper upper upper (yes 3 times) frame
            # but that would be nasty
            parent_locals = parent_frame.f_locals
            parent_a = parent_locals.get(a)
            parent_b = parent_locals.get(b)

            if None in (parent_a, parent_b):
                raise ValueError("Bad arguments to swap, perhaps you're trying to modify unbound local?")

        else:
            raise ValueError("Bad arguments to swap")

    # swap
    parent_locals[a], parent_locals[b] = parent_b, parent_a

    # write changes to frame's fastlocals so it persists
    pythonapi.PyFrame_LocalsToFast.argtypes = [py_object]
    pythonapi.PyFrame_LocalsToFast(parent_frame)
