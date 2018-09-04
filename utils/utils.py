from itertools import zip_longest


def iterate_by_batch(array_list, amount, fillvalue=None):
    args = [iter(array_list)] * amount
    return zip_longest(*args, fillvalue=fillvalue)