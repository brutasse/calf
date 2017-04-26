def chunked(items, chunk_size):
    acc = []
    for item in items:
        acc.append(item)
        if len(acc) >= chunk_size:
            yield acc
            acc = []
    yield acc
