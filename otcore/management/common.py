def substring_after(s, delimiter):
    return s.partition(delimiter)[2]


def substring_before(s, delimiter):
    return s.partition(delimiter)[0]
