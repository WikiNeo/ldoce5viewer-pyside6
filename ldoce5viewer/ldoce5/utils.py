def shorten_id(_id):
    ids = _id.split(".")
    if len(ids) == 4:
        return ".".join(ids[2:4])
    return _id
