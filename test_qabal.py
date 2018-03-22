import pytest
from qabal import Item, Session, inject

def foo(item):
    item['foo'] = 'foo'

def bar(item):
    item['bar'] = 'bar'

def baz(item):
    item['baz'] = 'baz'
    return item

def bar_baz(item):
    item['bar'] = 'bar!'
    item['baz'] = 'baz!'
    return item

def sig_based_analytic(bar, baz):
    return {'bar_baz': bar + baz}

def fubar(item):
    item['fubared'] = True

def analytic_with_metadata(bar):
    return bar + '?'

analytic_with_metadata.__inject__ = True
analytic_with_metadata.__trigger__ = Item['bar'] == 'bar'
analytic_with_metadata.__creates__ = 'bar'

def test_qabal_empty_route():
    sess = Session()
    res = sess.feed({'hello': 'world'})
    assert res['hello'] == 'world'

def test_qabal_empty_message():
    sess = Session()
    sess.add(foo, Item['type'] == 'foo')
    res = sess.feed({})
    assert len(res['__analytics__']) == 0

def test_qabal_simple_route():
    sess = Session()
    sess.add(foo, Item['type'] == 'foo')
    res = sess.feed({'type': 'foo'})
    assert res['foo'] == 'foo'
    assert res['type'] == 'foo'

def test_qabal_complex_route():
    sess = Session()
    sess.add(foo, Item['type'] == 'foo')
    sess.add(bar, Item['foo'] == 'foo')
    res = sess.feed({'type': 'foo'})
    assert res['bar'] == 'bar'

    sess.add(bar_baz, Item['foo'] == 'foo')
    res = sess.feed({'type': 'foo'})
    assert res['bar'] == 'bar!'

    sess.add(fubar, Item['baz'] == 'baz!')
    res = sess.feed({'type': 'foo'})
    assert res['fubared']

    res = sess.feed({'type': 'bar'})
    assert not res.get('fubared')

    sess.add(baz, Item['fubared'])
    res = sess.feed({'fubared': True})
    assert res['baz'] == 'baz'

    res = sess.feed({'type': 'foo'})
    assert res['baz'] == 'baz'
    assert res['bar'] == 'bar!'
    
    sess.add(inject(sig_based_analytic), Item['baz'] == 'baz!')
    res = sess.feed({'type': 'foo'})
    assert res['bar_baz'] == 'bar!baz!'

def test_qabal_remove():
    sess = Session()
    sess.add(foo, Item['type'] == 'foo')
    bar_trigger = sess.add(bar, Item['foo'] == 'foo')
    res = sess.feed({'type': 'foo'})
    assert res['bar'] == 'bar'
    sess.remove(bar_trigger)
    res = sess.feed({'type': 'foo'})
    print(res)
    assert res.get('bar') is None

def test_qabal_query_ast():
    assert Item['foo'].keys == ['foo']
    Item.keys = []
    trigger, _ = Item['foo'] == 'foo'
    assert trigger == 'foo'
    assert Item['foo']['bar'] == ['foo', 'bar']
    Item.keys = []
    trigger, test = Item['foo']['bar']['baz'] == 'foo'
    assert trigger == 'foo.bar.baz'
    assert test('foo')
    trigger, test = Item['foo']['bar']['baz'] > 5
    assert test(6)
    assert not test(5)
    trigger, test = Item['foo']['bar']['baz'] != 'foo' 
    assert test('foob')
    assert not test('foo')
    assert trigger == 'foo.bar.baz'

def test_analytic_metadata():
    sess = Session()
    sess.add(bar, Item['foo'] == 'foo')
    res = sess.feed({'foo': 'foo'})
    assert res['bar'] == 'bar'
    sess.add(analytic_with_metadata)
    res = sess.feed({'foo': 'foo'})
    assert res['bar'] == 'bar?'
    with pytest.raises(ValueError, message='Passing analytics without metadata and no route'):
        sess.add(foo)
    