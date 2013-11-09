import os


if OSError is not IOError:
    _FsErrors = (OSError, IOError)
else:
    _FsErrors = OSError


class DirectoryStore(object):
    def __init__(self, root):
        self.root = root
        self._create_dir(root)

    def _create_dir(self, d):
        if not (os.path.exists(d) and os.path.isdir(d)):
            os.mkdir(d)

    def get_file_object(self, key, create=False):
        if create:
            path = os.path.join(self.root, key[0:2])
            self._create_dir(path)
            path = os.path.join(path, key[2:4])
            self._create_dir(path)
            path = os.path.join(path, key)

            mode = 'wb'
        else:
            path = os.path.join(
                self.root,
                key[0:2],
                key[2:4],
                key
            )
            mode = 'rb'

        try:
            return open(path, mode)
        except _FsErrors:
            return None

    def exists(self, key):
        return os.path.exists(os.path.join(
            self.root,
            key[0:2],
            key[2:4],
            key
        ))
