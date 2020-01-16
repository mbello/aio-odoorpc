
def helper_build_kwargs(*, fields=None, limit=None, offset=None, order=None) -> dict or None:
    kwargs = dict()
    if offset is not None:
        kwargs['offset'] = offset
    if limit is not None:
        kwargs['limit'] = limit
    if order is not None:
        kwargs['order'] = order
    if fields is not None:
        kwargs['fields'] = fields
    return kwargs if kwargs else None
