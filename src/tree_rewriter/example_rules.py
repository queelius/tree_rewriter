def variable_substitution(node, ctx):
    """
    Rewrite a node by replacing a variable with a constant value if the variable
    name is in the context.

    For instance, suppose in the context, we have the node
        
        {'x': {'type': 'constant', 'value': 3, 'children': []}}

    and node['value'] is 'x'. Then, the node is replaced by

        {'type': 'constant', 'value': 3, 'children': []}

    :param node: a node
    :param ctx: a context
    :return: a new node
    """
    if node['type'] != 'variable' or node['value'] not in ctx:
        return node
    
    return ctx[node['value']]

def sum_remove_zeros(node, ctx):
    """
    If a node is a sum, remove any zeros in the arguments.

    :param node: a node
    :param ctx: a context
    :return: a new node
    """
    if node['type'] != '+' and node['type'] != '-' and node['type'] != 'sum':
        return node
    
    node.children = [child for child in node.children() if (child['value'] != 0 and child['type'] != 'constant') or child['type'] != 'constant']
    if len(node.children) == 1:
        return node.children[0]
    return node    

def max_simplify(node, ctx):
    """
    If a node is a max, simplify the arguments.

    :param node: a node
    :param ctx: a context
    :return: a new node
    """

    if node['type'] != 'max':
        return node
    
    max_value = max([child['value'] for child in node.children() if child['type'] == 'constant'])
    node.children = [child for child in node.children() if (child['type'] == 'constant' and child['value'] == max_value) or child['type'] != 'constant']
    if len(node.children) == 1:
        return node.children[0]
    return node


def min_simplify(node, ctx):
    """
    If a node is a min, simplify the arguments.

    :param node: a node
    :param ctx: a context
    :return: a new node
    """

    if node['type'] != 'min':
        return node
    
    min_value = min([child['value'] for child in node.children() if child['type'] == 'constant'])
    node.children = [child for child in node.children() if (child['type'] == 'constant' and child['value'] == min_value) or child['type'] != 'constant']
    if len(node.children) == 1:
        return node.children[0]
    return node

def prod_remove_ones(node, ctx):
    """
    If a node is a product, remove any ones in the arguments.

    :param node: a node
    :param ctx: a context
    :return: a new node
    """
    if node['type'] != '*' and node['type'] != '/':
        return node    

    node.chidlren = [child for child in node.children() if (child['value'] != 1 and child['type'] != 'constant') or child['type'] != 'constant']
    if len(node.children) == 1:
        return node.children[0]
    return node

