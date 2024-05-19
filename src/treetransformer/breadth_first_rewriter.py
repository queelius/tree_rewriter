
class BreadthFirstRewriter:
    """
    Applies a function to the nodes in the tree using breadth-first traversal strategy.
    Conceptually, it is a function of type

        BreadthFirstRewriter[fn] : Tree -> Tree

    where Tree is a tree data structure that supports:

    - `children()` method that returns a list of child nodes.
    - `add_child(node)` method that adds a child node.

    The function `fn` is of type `Node -> Node`, where Node is
    a node in the tree (often, the node itself models the conept of a tree).
    """

    def __init__(self, proc, max_depth=None):
        """
        `proc` is a procedure that takes in a Node and does some arbitrary computation,
        where Node is a node in the tree. The `proc` likely produces side-effects,
        e..g., printing or transforming each node visited in some way.

        :param fn: Function to apply to each node. Should accept two arguments: the node and the context.
        :param max_depth: Maximum depth to traverse. If None, traverses the entire tree.
        """
        self.fn = fn
        self.max_depth = max_depth

    def visit(self, node) -> None:
        """
        Visit a node in the tree and apply the function to it and its children
        recursively, in postorder (bottom-up) strategy.

        :param node: The node to visit.
        :return: The new node after applying the function recursively, bottom-up.
        """
        queue = deque([(self, 0)])
        while queue:
            node, depth = queue.popleft()
            fn(node)
            if self.max_depth is not None and depth >= self.max_depth:
                break
            queue.extend((child, depth + 1) for child in node.children())

    def __call__(self, tree) -> None:
        self.visit(tree)
