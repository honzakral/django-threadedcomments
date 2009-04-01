def annotate_tree_properties(comments):
    """
    iterate through nodes and adds some magic properties to each of them
    representing opening list of children and closing it
    """
    if not comments:
        return

    it = comments.iterator()

    # get the first item, this will fail if no items !
    old = it.next()

    # first item starts a new thread
    old.open = 1
    last = set()
    for c in it:
        # if this comment has a parent, store it's last child for future reference
        if old.last_child_id:
            last.add(old.last_child_id)

        # this is the last child, mark it
        if c.pk in last:
            c.last = True

        # increase the depth
        if c.depth > old.depth:
            c.open = 1

        else: # c.depth <= old.depth
            # close some depths
            old.close = range(old.depth - c.depth)

            # new thread
            if old.root_id != c.root_id:
                # close even the top depth
                old.close.append(len(old.close))
                # and start a new thread
                c.open = 1
                # empty the last set
                last = set()
        # iterate
        yield old
        old = c

    old.close = range(old.depth)
    yield old
