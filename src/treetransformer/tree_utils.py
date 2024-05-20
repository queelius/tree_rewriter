from collections import deque, defaultdict

def breadth_first(node,
                  proc_node=None,
                  proc_node_at_lvl=None,
                  proc_lnk=None) -> dict:
    """
    Performs a breadth-first traversal on the tree rooted at the given node.
    Custom computations can be done via `proc_node`, `proc_node_at_lvl` and
    `proc_lnk` functions.

    The algorithm assumes the tree has the following method:

    - 'children()': returns a list of children of the given node.

    tree: A tree-like data structure.
    proc_node: A function to process nodes (optional).
    proc_node_at_lvl: A function to process nodes at each level (optional).
    proc_link: A function to process each link (optional).
    """
    q = deque([(node, 0)])  # (node, level)
    lvl_info = defaultdict(int)  # Dictionary to store information per level
    lnk_info = defaultdict(list)  # Dictionary to store information per link
    node_info = defaultdict(list)  # Dictionary to store information per node

    while q:
        cur, level = q.popleft()
        
        # Process the current node at the given level
        if proc_node_at_lvl:
            proc_node_at_lvl(cur, level, lvl_info)

        if proc_node:
            proc_node(cur, node_info)
        
        for child in cur.children():
            q.append((child, level + 1))
            if proc_lnk:
                proc_lnk(cur, child, lnk_info)

    return node_info, lvl_info, lnk_info

def tree_width(tree):

    def width_helper(_, lvl, lvl_info):
        lvl_info[lvl] += 1

    _, lvl_info, _ = breadth_first(tree, proc_node_at_lvl=width_helper)
    return max(lvl_info.values())

def node_depth_from_root(node):
    """
    Find the depth of the node by traversing the tree upwards.

    Assumes the tree has the following method:

    - 'get_parent()': returns the parent of the node.
    
    node: The node to start the traversal from.
    
    Returns the depth of the node at the root, and the root node.
    """
    depth = 0
    while node.get_parent():
        node = node.get_parent()
        depth += 1
    return depth, node

def nodes_at_level(node):

    """
    Find all nodes at the specified level using breadth_first traversal.
    
    node: The root node of the tree.
    target_level: The level to find nodes at.
    
    Returns a list of nodes at the specified level.
    """
    def _collect_node_lvl(node, lvl, lvl_info):
        lvl_info[lvl].append(node)

    target_lvl, root = node_depth_from_root(node)
    _, lvl_info, _ = breadth_first(root, proc_node_at_lvl=_collect_node_lvl)
    return lvl_info[target_lvl] if target_lvl in lvl_info else []



class TreeAlg:
    """
    Class containing tree algorithms.

    These algorithms are designed to work with any tree representation that
    implements the following methods:

    - `children()`: Get the children of a node.
    - `add_child(child)`: Add a child to a node.
    """

    @staticmethod
    def depth(tree) -> int:
        """
        Get the depth of tree.

        :param tree: The tree.
        :return: Integer representing the depth of the tree.
        """
        return 1 + max([TreeAlg.depth(c) for c in tree.children()], default=0)
    
    @staticmethod
    def width(tree) -> int:
        """
        Get the width of tree.

        :return: Integer representing the width of the tree.
        """
        # base case: if we have a leaf node, the width is 1
        if TreeAlg.is_leaf(tree):
            return 1

        # otherwise, at a partiular node, the width is computed
        # by finding the number of children at each level
        # and summing them up and returning the maximum

        # get the children of the current node
        children = tree.children()

        # get the width of the children
        children_width = [TreeAlg.width(c) for c in children]

        # return the sum of the children width
        return sum(children_width)
    


    @staticmethod
    def is_leaf(node) -> bool:
        """
        Determine if a node (tree) is a leaf.

        :return: True if the node is a leaf, False otherwise.
        """
        return not node.children()


    def filter_tree(tree, pred) -> List
        """
        Return nodes in tree satisfying `pred` where `pred` is a predicate on tree nodes.

        :param tree : The tree
        :param pred : A function that takes a node and returns True if the node matches the condition.
        :return: Nodes that match on pred.
        """

        results = []
        def _filter(node):

            if pred(node):
                results.append(node)
            for child in node.children():
                _match(child)

        _filter(tree)
        return results
