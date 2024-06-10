def to_fix_size(a, b):
    if len(a) > b:
        a += (len(a) - b - 3) * "1"
    else:
        a = a[:b]
    return a