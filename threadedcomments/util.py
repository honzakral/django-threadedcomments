def annotate_tree_properties(comments):
    """
    iterate through nodes and adds some magic properties to each of them
    representing opening list of children and closing it
    """
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

        # increase the level
        if c.level > old.level:
            c.open = 1

        else: # c.level <= old.level
            # close some levels
            old.close = range(old.level - c.level)

            # new thread
            if old.root != c.root:
                # close even the top level
                old.close.append(len(old.close))
                # and start a new thread
                c.open = 1
                # empty the last set
                last = set()
        # iterate
        yield old
        old = c

    old.close = range(old.level)
    yield old