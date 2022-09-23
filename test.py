from swap import swap


foo = "foo"
bar = "bar"

swap(foo, bar)

assert foo == "bar" and bar == "foo"

def f():
    a = keeper = object()
    b = "banana"
    swap(a, b)
    assert a == "banana" and b == keeper

    def g():
        nonlocal a
        nonlocal b
        swap(a, b)

    g()
    assert b == "banana" and a == keeper

f()

try:
    swap("banana", 1)
    swap(object(), foo)
    swap([1,2,3], (""))
    raise AssertionError("Unreachable. It should've raised a ValueErrornreachable")
except ValueError:
    pass
