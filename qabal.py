from inspect import signature

class _QueryAST:
    """
    Internal class that implements the Qabal query language for content-based queries.
    Converts Python query expressions to tuples that are injested by the content-based router.
    """
    keys = []

    def _create_ast_node(self, test):
        res = '.'.join(self.keys), test
        self.keys = []
        return res

    def __getitem__(self, key):
        self.keys.append(key)
        return self

    def __eq__(self, other):
        return self._create_ast_node(lambda target: target == other) 

    def __le__(self, other):
        return self._create_ast_node(lambda target: target <= other)

    def __lt__(self, other):
        return self._create_ast_node(lambda target: target < other)

    def __ne__(self, other):
        return self._create_ast_node(lambda target: target != other)
    
    def __ge__(self, other):
        return self._create_ast_node(lambda target: target >= other)

    def __gt__(self, other):
        return self._create_ast_node(lambda target: target > other)

    def __contains__(self, other):
        return self._create_ast_node(lambda target: other in target)

Item = _QueryAST()


class ItemData(dict):
    """
    Qabal injects this object into analytics that take in the content dictionary.
    Has the same interface as a dict, so it can be used by code that is unaware of Qabal.
    """
    
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        self.changes = []
        dict.__setitem__(self, '__analytics__', [])

    def __setitem__(self, name, val):
        self.changes.append((name, val))
        dict.__setitem__(self, name, val)
    
    def __delitem__(self, name):
        raise KeyError('Deleting content in an analytic is not yet supported.')


class Session:
    """
    A Qabal session is a collection of subscribable queries and analytics that trigger 
    when a content dictionary is changed.
    """
    def __init__(self):
        self.triggers = {}

    def feed(self, content):
        """
        Feed in a new content dict. Any fields in this initial dict count as 
        subscribable routes.
        """
        item = ItemData(content)
        item.changes = [(k,v) for k,v in content.items()]
        return self._route(item)
    
    def _route(self, content):
        # Routing is done when there are no more routes to handle.
        if not content.changes:
            return content       
        analytics = []
        # Go through every subscribable route.
        for k, v in content.changes:
            evt = self.triggers.get(k)
            if evt:
                # Append all the analytics that are relevant to this route.
                for trigger, analytic in evt:
                    if trigger(v):
                        analytics.append(analytic) 
        changes = []
        # Now execute the analaytics that we found.
        for analytic in analytics:
            # Step one for provenance support.
            content['__analytics__'].append(analytic)
            content.changes.clear()
            res = analytic(content)
            # This allows for some flexibility in APIs
            if type(res) is dict:
                changes.extend(res.items())
                content.update(res)
            else:
                changes.extend(content.changes)
        content.changes = changes
        return self._route(content)
        
    def add(self, analytic, on=None):
        """
        Add a new analytic to the session.
        """
        # Analytics can include routing metadata. 
        # If the analytic has routing metadata, the second param is optional.
        if not on and not hasattr(analytic, '__trigger__'):
            raise ValueError('Route must be defined if analytic does not have route metadata.')
        if hasattr(analytic, '__trigger__'):
            trigger, test = analytic.__trigger__
        if hasattr(analytic, '__inject__') and analytic.__inject__:
            analytic = inject(analytic)

        if type(on) is _QueryAST:
            trigger = '.'.join(on.keys)
            on.keys = []
            test = lambda target: target
        elif on:
            trigger, test = on
        trigger_evt = self.triggers.get(trigger)
        trigger_params = (test, analytic)
        if trigger_evt:
            self.triggers[trigger].append(trigger_params)
        else:
            self.triggers[trigger] = [(trigger_params)]
        return (trigger, trigger_params)
    
    def remove(self, handle):
        """
        Delete a new analytic from the session. Requires the return value of add as input to handle.
        """
        trigger, val = handle
        self.triggers[trigger].remove(val)

def inject(func):
    """
    Primitive to inject dict values as signature elements, useful for more fluent APIs.
    """
    sig = signature(func)

    def _wrapped(item):
        # This computes the intersection between the signature of the wraped func and the content dictionary
        intersection = {key:item[key] for key in [param.name for param in sig.parameters.values()]}
        return func(**intersection)
    
    return _wrapped
