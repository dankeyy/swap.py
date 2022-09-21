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

f()

# correctly fails with ValueError: Bad arguments to swap:
# swap("banana", 1)
# swap(object(), foo)
# swap([1,2,3], (""))
