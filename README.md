# swap.py
CPP-std::swap-like swap for CPython\
🔴 Note - this heavily relies on c-api; will break for other implementations of Python. 🔴
## What
```python
from swap import swap

def f():
    a = 'foo'
    b = 'bar'
    
    swap(a, b)
    
    print(f'{a = }\n{b = }')
    
f() 
```

```console
$ python test.py
a = 'bar'
b = 'foo'
```
###### An example without a function call wouldn't show as much because globals are easier to carve through <br />

## You know you could just do `a, b = b, a` right?
Right

## Why
Why not \
Was a nice experiment too

## How
Swapping the two variables entry at the frame's locals.

## But I thought locals is only a copy and you can't really change a function's locals at runtime
When there's a will, there's a way. That way is c-api.

So after we change locals, we rewrite those to the frame's fastlocals (what is behind your friendly neighborhood `locals`). 
That's really all there is to it. Simple than you might have thought, huh?

Also, I feel obliged to say it at this point; this is an undocumented function of the c-api created mainly (only?) for debuggers.\
But as the shitposter I am, I'm going to abuse it (sorry).\
So maybe don't do this at home, do as I say, not as I do, yada yada.
 
 ## Wouldn't you need to have the arguments' original names to access them at locals' dictionary
 Yea and that part can be a little tricky.
 Though a simple implementation would've just taken the call line string from the outer frame and regex out the variables' names.\
 But-\
 That breaks in case the call is spreaded over multiple lines.\
 Generally I don't think it's a big deal for a function like swap (only two variable-arguments, hard to believe you'd need more than one line for it).\
 But it just so happens in the last couple of days I wrote an implementation to carve out function call
 arguments representation (agnostic of newlines, see [here](https://github.com/dankeyy/arg_repr.py/)), so I used that.\
 It's a bit lengthier than the alternative, but should generally work or raise ValueError for bad arguments/ bad number of arguments.
