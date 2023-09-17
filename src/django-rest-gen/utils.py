import os


def empty_fpath(fpath):
    """
    Whether the given path is empty or not
    :param fpath:
    :return:
    """
    empty = True
    if os.path.exists(fpath):
        with open(fpath) as f:
            content = f.read()
            if content.strip() != "":
                empty = False
    return empty