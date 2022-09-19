from swap import swap


foo = "foo"
bar = "bar"

swap(foo, bar)

assert foo == "bar" and bar == "foo"
