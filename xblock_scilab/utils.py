import hashlib
import os

from functools import partial


def get_sha1(file_handler):
    BLOCK_SIZE = 2**10 * 8  # 8kb
    sha1 = hashlib.sha1()
    for block in iter(partial(file_handler.read, BLOCK_SIZE), ''):
        sha1.update(block)
    file_handler.seek(0)
    return sha1.hexdigest()


def file_storage_path(location, sha1, filename):
    # pylint: disable=no-member
    """
    Get file path of storage.
    """
    path = (
        '{loc.org}/{loc.course}/{loc.block_type}/{loc.block_id}'
        '/{sha1}{ext}'.format(
            loc=location,
            sha1=sha1,
            ext=os.path.splitext(filename)[1]
        )
    )
    return path
