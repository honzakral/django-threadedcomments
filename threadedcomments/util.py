from itertools import chain, imap

__all__ = ['fill_tree', 'annotate_tree_properties', ]

def _mark_as_root_path(comment):
    " Mark on comment as Being added to fill the tree. "
    setattr(comment, 'added_path', True)
    return comment

def fill_tree(comments):
    """
    Prefix the comment_list with the root_path of the first comment. Use this
    in comments' pagination to fill in the tree information.
    """
    if not comments:
        return

    it = iter(comments)
    first = it.next()
    return chain(imap(_mark_as_root_path, first.root_path), [first], it)

def annotate_tree_properties(comments):
    """
    iterate through nodes and adds some magic properties to each of them
    representing opening list of children and closing it
    """
    if not comments:
        return

    it = iter(comments)

    # get the first item, this will fail if no items !
    old = it.next()

    # first item starts a new thread
    old.open = True
    last = set()
    for c in it:
        # if this comment has a parent, store its last child for future reference
        if old.last_child_id:
            last.add(old.last_child_id)

        # this is the last child, mark it
        if c.pk in last:
            c.last = True

        # increase the depth
        if c.depth > old.depth:
            c.open = True

        else: # c.depth <= old.depth
            # close some depths
            old.close = range(old.depth - c.depth)

            # new thread
            if old.root_id != c.root_id:
                # close even the top depth
                old.close.append(len(old.close))
                # and start a new thread
                c.open = True
                # empty the last set
                last = set()
        # iterate
        yield old
        old = c

    old.close = range(old.depth)
    yield old
