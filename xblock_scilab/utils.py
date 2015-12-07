from functools import partial

import hashlib
import os


def get_sha1(file_handler):
    BLOCK_SIZE = 2**10 * 8  # 8kb
    sha1 = hashlib.sha1()
    for block in iter(partial(file_handler.read, BLOCK_SIZE), ''):
        sha1.update(block)
    file_handler.seek(0)
    return sha1.hexdigest()


def file_storage_path(url, sha1, filename):
    assert url.startswith("i4x://")
    path = url[6:] + '/' + sha1
    path += os.path.splitext(filename)[1]
    return path