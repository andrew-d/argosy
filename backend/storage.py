import os
import hashlib
from io import BytesIO
from werkzeug import secure_filename


class FileNotFoundException(KeyError):
    """This exception is raised when a file is not found."""
    def __init__(self, id):
        super(FileNotFoundException, self).__init__(
            "The file with id '%s' was not found" % (id,)
        )


class FileStorageBase(object):
    HASH_ALGORITHM = 'sha256'

    def save_new(self, file_data):
        # Hash the data.
        key = hashlib.new(self.HASH_ALGORITHM, file_data).hexdigest()

        # Save with this key.
        return self.save_with_key(key, file_data)

    def save_with_key(self, key, file_data):
        raise NotImplementedError('This method is not implemented in the base '
                                  'class!')

    def get(self, id):
        raise NotImplementedError('This method is not implemented in the base '
                                  'class!')


class MemoryFileStorage(FileStorageBase):
    def __init__(self):
        self.cache = {}

    def save_with_key(self, key, file_data):
        self.cache[key] = file_data
        return key

    def get(self, id):
        if id not in self.cache:
            raise FileNotFoundException(id)

        return BytesIO(self.cache[id])


class DirectoryFileStorage(FileStorageBase):
    def __init__(self, base_dir, depth=2):
        self.base_dir = os.path.abspath(base_dir)
        self.depth = depth

    def _get_path(self, key):
        # Firstly, use the depth parameter to find out how many path segments
        # we are to split the key into.
        segs = []
        for i in range(self.depth):
            segs.append(key[i*2:i*2 + 2])

        # Ensure the path exists.
        dir_path = os.path.join(self.base_dir, *segs)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Get the actual path.
        return os.path.join(dir_path, secure_filename(key))

    def save_with_key(self, key, file_data):
        path = self._get_path(key)
        with open(path, 'wb') as f:
            f.write(file_data)

        return key

    def get(self, id):
        path = self._get_path(id)
        try:
            f = open(path, 'rb')
        except (IOError, OSError):
            raise FileNotFoundException(id)

        return f
