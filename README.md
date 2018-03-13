# Qabal

Qabal is a simple and fast open source content-based message broker. Use Qabal to organize all your multi-stage analytical workloads. 

Qabal has no install dependencies outside of the default Python runtime. Use it on your Raspberry Pi, laptop, or 100 node Dask cluster. Routing decisions in Qabal take constant time, so you can use it for complex multistage analytics with thousands of steps. It's lightweight, simple to understand, easy to integrate with distributed task libraries (eg. Dask) and fast to execute.

Qabal analytics need not be aware that they are part of a message broker pipeline. They don't need to depend or import any Qabal library. The data structure used in routing extends the standard Python dictionary. Qabal comes with ready to use reflection-based content injection, giving users flexibility on the API of their analytics.

### Installation

```
pip install qabal
```

### Example

Qabal has a simple API that revolves around attaching functions to a Session object.

```python
from qabal import Session, Item

def foo(item):
    item['foo'] = 'foo'
    return item

def bar(item):
    item['bar'] = 'bar'
    return item

def baz(item):
    item['baz'] = 'baz'
    return item

def bar_baz(item):
    item['bar'] = 'bar!'
    item['baz'] = 'baz!'
    return item

def parameters_are_okay_too(foo, bar):
    return {'baz': foo+bar}

sess = Session()
sess.add(foo, Item['type'] == 'foo')
sess.add(bar, Item['foo'] == 'foo')
res = sess.feed({'type': 'foo'})

# The session is mutable at any time.
bar_baz = sess.add(bar_baz, Item['bar'] == 'bar')
res = sess.feed({'type': 'foo'})
sess.remove(bar_baz)
```