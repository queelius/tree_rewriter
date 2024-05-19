class PreorderRewriter:
    """
    Applies a function to the nodes in the tree using some traversal strategy.
    Conceptually, it is a function of type

        PreorderRewriter[fn] : Tree -> Tree

    where Tree is a tree data structure that supports:
    
    - `children()` method that returns a list of child nodes.
    - `add_child(node)` method that adds a child node.

    The function `fn` is of type `Node, Context -> Node, Context`, where Node is
    a node in the tree (often, the node itself models the conept of a tree) and
    Context represents information the function can use and modify, but for
    which the modifications only affect the current node and its children.
    """

    def __init__(self, fn, max_depth=None):
        """
        `fn` is a function of type `Node, Context -> Node, Context`, where Node
        is a node in the tree and Context is information that `fn` can use and
        modify, but any modifications only affect the current node and its
        children. (It can affect the current node by affecting its children.)

        :param fn: Function to apply to each node. Should accept two arguments: the node and the context.
        :param max_depth: Maximum depth to traverse. If None, traverses the entire tree.
        """
        self.fn = fn
        self.max_depth = max_depth

    def visit(self, node, ctx=None, depth=0):
        """
        Visit a node in the tree and apply the function to it and its children
        recursively, in preorder (top-down) traversal.

        :param node: The node to visit.
        :param ctx: Context to pass to the function.
        :param depth: The depth of the current node in the tree.
        :return: The new node after applying the function recursively, top-down.
        """
        if self.max_depth is not None and depth > self.max_depth:
            return node
        
        node, ctx = self.fn(node, ctx)
        childs = [self.visit(child, ctx, depth + 1) for child in node.children()]

        # we need to remove the old children first
        for child in node.children():
            node.remove_child(child)
        for child in childs:
            node.add_child(child)
        return node
    
    def __call__(self, tree, ctx=None):
        return self.visit(tree, ctx, 0)