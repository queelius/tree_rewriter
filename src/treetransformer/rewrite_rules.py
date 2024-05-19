def rewrite_repeated_application(ops = {'+': '*', '*': '**'}):
    """
    Simplify a tree by replacing repeated application of an operator with a
    single application of its "exponentiated" form.

    Here is the pattern: (op e1 e1 e1 e2 e2) =>
        (op (exponentiated(op) e1 3) (exponentiated(op) e2 2))l

    Assumption: the operator is associative and commutative.

    :param ops: a key-value pair of operator and its exponentiated form
    :return: a function that takes a node and a context and returns a new node
    """

    def _simplify(node, ctx):

        if node['type'] not in ops:
            return node
    
        childs = node.children()

        # let's find children that are the same (==). since the operator is
        # associative and commutative, we can pull all the same children together
        # and count them. let's put them all in a dictionary:
        #
        #    { child_value: count, ... }
        # the count can be 1, 2, 3, ...
        same_childs = []
        for child in childs:
            if child in same_childs:
                continue
            count = sum([child == c for c in childs])
            same_childs.append((child, count))
        
        # if there is no repeated child, we can return the node as is
        if len(same_childs) == len(childs):
            return node

        # let's create a new node with the repeated children replaced with the
        # exponentiated form
        new_childs = []
        for child, count in same_childs:
            if count == 1:
                new_childs.append(child)
            else:
                new_childs.append(nt.NestedTree(
                    type=ops[node['type']],
                    children=[child, nt.NestedTree(type='const', value=count)]))
                
        return nt.NestedTree(type=node['type'], children=new_childs)

    return _simplify

def make_substitutions(node, ctx):
    """
    Rewrite a tree by substituting variables with their expression in the context.

    Suppose we have a leaf node `NestedTree(type='var', value='x')`. We consider
    two kinds of substitutions:

    1) If in the context we have an entry `{..., 'x': 1, ...}`
       we replace the leaf node with the constant value:
       `NestedTree(type='const', value=1)`. Any other value can also be used,
       with the exception of a `NestedTree` expression.

    2) If in the context, we have an entry `{..., 'x': NestedTree(...), ...}`,
       we replace the leaf node with the NestedTree. This allows for more
       complicated substitutions, like:
           `{ 'x' : NestedTree(type='+', children=[
                NestedTree(type='var', value='y'),
                NestedTree(type='const', value=1)]) }`.
    
    :param node: a node
    :param ctx: a context
    """
    if node['type'] != 'var' or node['value'] not in ctx or not node.is_leaf():
        return node
    
    value = ctx[node['value']]
    if isinstance(value, nt.NestedTree):
        return value
    else:
        return nt.NestedTree(type='const', value=value)

def simplify_identities(ops = {'+': 0, '*': 1, 'max': -float('inf')}):
    """
    Simplify a tree by removing identities from the leaf nodes of an operator.

    Example: (+ [x]) => x
             (+)     => 0

    :param ops: a key-value pair of operator and its identity
    :return: a function that takes a node and a context and returns a new node
    """
    def _simplify(node, ctx):
        op = node['type']
        if op not in ops:
            return node
        
        if node.is_leaf():
            return nt.NestedTree(type='const', value=ops[op])
        if len(node.children()) == 1:
            return node.children()[0]
        else:
            return node
    return _simplify

def simplify_reduce(ops = {'max': max,
                           '+': sum,
                           '*': lambda x: reduce(lambda x, y: x * y, x, 1)}):
    """
    Simplify a tree by reducing the leaf nodes of an operator to a single value
    using the operator itself.

    Example:

        (max [1, x, -2, y]) => (max [x, y, eval(max [1, -2])] => (max [x, y, 1])

    :param ops: a key-value pair of operator and a function that takes a list of values
    :return: a function that takes a node and a context and returns a new node
    """

    def _simplify(node, ctx):
        
        if node['type'] not in ops:
            return node

        values = [child for child in node.children() if child.is_leaf()]
        if len(values) <= 1:
            node

        # apply op to the values
        op = ops[node['type']]
        value = op([child['value'] for child in values])
        exprs = [child for child in node.children() if not child.is_leaf()]
        return nt.NestedTree(type=op, children=exprs + [nt.NestedTree(type='const', value=value)])

    return _simplify
