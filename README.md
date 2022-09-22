# swap.py
cpp-std::swap-like swap function for cpython

## 🔴 Caveats 🔴
This implementation heavily relies on c-api; will not work for other implementations of Python.

So generally works fine for all versions of cpython (even 2.7).\
But - if for some reason you spread your swap call over multiple lines,\
you would need to either use a version newer than 3.7 (old parser issue) or one-line it.

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

So after we swap the entries of (say) `a` and `b` in the frame's `f_locals` (this is what you would've got through locals() if you were at the actual frame), we write those to the frame's fastlocals (what is behind your friendly neighborhood `locals`) so that the change will persist after exiting the current frame.\
I will make it clear that all this of course is not possible with merely `f_locals`/ `locals()` which really are just a dict representation, given by demand, to the frame's fastlocals array. That's why we need c-api's fasttolocals to make it stick.\
Overall that's really all there is to it. Pretty simple when you think about it.

Also, I feel obliged to say it at this point; this is using an undocumented function of the c-api created mainly (only?) for debuggers.\
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
