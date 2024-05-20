from collections import deque, defaultdict

def breadth_first_walker(
        root,
        proc_node=None,
        proc_node_at_lvl=None,
        proc_lnk=None) -> dict:
    """
    Performs a breadth-first walker on the tree rooted at root.
    Custom computations can be done via `proc_node`, `proc_node_at_lvl` and
    `proc_lnk` functions.

    The algorithm assumes the tree has the following method:

    - 'children()': returns a list of children of the given node.

    tree: A tree-like data structure.
    proc_node: A function to process nodes (optional).
    proc_node_at_lvl: A function to process nodes at each level (optional).
    proc_link: A function to process each link (optional).
    """
    q = deque([(root, 0)])  # (node, level)
    lvl_info = defaultdict(int) if proc_node_at_lvl else None
    lnk_info = defaultdict(list) if proc_lnk else None
    node_info = defaultdict(list) if proc_node else None

    while q:
        cur, level = q.popleft()

        if proc_node:
            proc_node(cur, node_info)

        # Process the current node at the given level
        if proc_node_at_lvl:
            proc_node_at_lvl(cur, level, lvl_info)
        
        for child in cur.children():
            q.append((child, level + 1))
            if proc_lnk:
                proc_lnk(cur, child, lnk_info)

    return node_info, lvl_info, lnk_info

def tree_width(tree):

    def width_helper(_, lvl, lvl_info):
        lvl_info[lvl] += 1

    _, lvl_info, _ = breadth_first_walker(tree, proc_node_at_lvl=width_helper)
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
    def _collect_lvl(node, lvl, lvl_info):
        lvl_info[lvl].append(node)

    target_lvl, root = node_depth_from_root(node)
    _, lvl_info, _ = breadth_first_walker(root, proc_node_at_lvl=_collect_lvl)
    return lvl_info[target_lvl] if target_lvl in lvl_info else []

