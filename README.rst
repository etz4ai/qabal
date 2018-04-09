Qabal
=====

Qabal is a simple and fast open source content-based message broker. Use
Qabal to organize all your multi-stage analytical workloads.

Qabal has no install dependencies outside of the default Python runtime.
Use it on your Raspberry Pi, laptop, or 100 node Dask cluster. Routing
decisions in Qabal take constant time, so you can use it for complex
multistage analytics with thousands of steps. It’s lightweight, simple
to understand, easy to integrate with distributed task libraries (eg.
Dask) and fast to execute. It has configurable full pipeline data
provenance. In extended provenance mode, Qabal records when every data
item is added or updated by what analytic and at what time.

Qabal analytics need not be aware that they are part of a message broker
pipeline. They don’t need to depend or import any Qabal library. The
data structure used in routing extends the standard Python dictionary.
Qabal comes with ready to use reflection-based content injection, giving
users flexibility on the API of their analytics.

Installation
~~~~~~~~~~~~

::

    pip install qabal

Try It For Yourself
~~~~~~~~~~~~~~~~~~~

Qabal has a simple API that revolves around attaching functions to a
Session object.

You define routes in Qabal using a query DSL that resembles Python
conditional statements. These get “compiled” into more traditional
message broker routes.

.. code:: python

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

    # If your trigger query doesn't use the Qabal query language, an analytic need not even depend on Qabal.
    class AnalyticWithMetadata:
        __trigger__ = Item['baz'] == 'baz!'
        __inject__ = True
        __creates__ = 'qux'

        def __call__(self, baz):
            return baz + '?'

    example = AnalyticWithMetadata()
    # Despite all the Qabal metadata, this analytic still maintains a normal API. 
    print(example('hello')) # Outputs: 'hello?'

    sess = Session(provenance='extended') # Qabal records a ton of information in this mode.
    sess.add(foo, Item['type'] == 'foo')
    sess.add(bar, Item['foo'] == 'foo')
    res = sess.feed({'type': 'foo'})
    print(res)
    print(res.provenance)

    # The session is mutable at any time.
    handle = sess.add(bar_baz, Item['bar'] == 'bar')
    res = sess.feed({'type': 'foo'})
    sess.remove(handle)
    print(res)

    sess.add(bar_baz, Item['bar'] == 'bar')
    # Analytics with metadata don't need a route
    sess.add(example)
    res = sess.feed({'type': 'foo'})
    print(res)
