import hashlib
import datetime
from contextlib import closing

import falcon
from werkzeug.formparser import parse_form_data
from PIL import Image

from . import json
from . import config
from . import models
from .store import DirectoryStore


PAGE_SIZE = 20


class BaseResource(object):
    def __init__(self, db, image_store, thumb_store):
        self.db = db
        self.image_store = image_store
        self.thumb_store = thumb_store


class ItemsResource(BaseResource):
    def on_get(self, req, resp):
        page = req.get_param_as_int('page') or 0
        items = models.Item.select().order_by(models.Item.hash).paginate(page, PAGE_SIZE)

        resp.body = json.dumps({
            'page': page,
            'items': list(x.to_dict() for x in items),
        })
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        stream, form, files = parse_form_data(req.env)

        # Find file with the given name.
        uploaded_file = files.get('upload')
        if uploaded_file is None:
            raise falcon.HTTPBadRequest('Invalid request',
                                        'No uploaded file was found.  Ensure '
                                        'that the name of the field is '
                                        '"upload"')

        # Validate file
        if not uploaded_file.mimetype.startswith('image/'):
            raise falcon.HTTPBadRequest('Invalid upload',
                                        'Bad mimetype for upload.  The '
                                        'mimetype must be an image.')

        # Read file data.
        file_data = uploaded_file.read()

        # Hash the file.
        h = hashlib.sha256()
        h.update(file_data)
        file_hash = h.hexdigest()

        uploaded_file.seek(0)

        try:
            i = models.Item.get(models.Item.hash == file_hash)
            resp.status = falcon.HTTP_409   # Conflict
        except models.Item.DoesNotExist:
            # Create an image from the file data.
            img = Image.open(uploaded_file)

            # Save this image to the data directory.
            with closing(self.image_store.get_file_object(file_hash, create=True)) as new_image:
                img.save(new_image, format='PNG')

            # Create thumbnail.
            thumb = img.resize((128, 128))

            # Save the thumbnail.
            with closing(self.thumb_store.get_file_object(file_hash, create=True)) as new_thumb:
                thumb.save(new_thumb, format='PNG')

            i = models.Item(
                hash=file_hash,
                created_on=datetime.datetime.utcnow(),
                file_size=len(file_data),
                width=img.size[0],
                height=img.size[1]
            )
            i.save(force_insert=True)

            resp.status = falcon.HTTP_201

        resp.body = json.dumps(i.to_dict())


class ItemResource(BaseResource):
    def on_get(self, req, resp, item_id):
        try:
            item = models.Item.get(models.Item.hash == item_id)
        except models.Item.DoesNotExist:
            raise falcon.HTTPNotFound()

        resp.body = json.dumps(item.to_dict())
        resp.status = falcon.HTTP_200


class ItemDataResource(BaseResource):
    def on_get(self, req, resp, item_id):
        try:
            item = models.Item.get(models.Item.hash == item_id)
        except models.Item.DoesNotExist:
            raise falcon.HTTPNotFound()

        if req.path.endswith('/data'):
            store = self.image_store
        elif req.path.endswith('/thumb'):
            store = self.thumb_store
        else:
            raise ValueError("Bad type: %s" % (req.path,))

        with closing(store.get_file_object(item.hash)) as data_file:
            resp.body = data_file.read()
        resp.status = falcon.HTTP_200
        resp.content_type = 'image/png'



app = falcon.API()

db = models.bind_db(config.get_db())
db.connect()

opts = {
    'db': db,
    'image_store': DirectoryStore(config.IMAGE_STORE_DIR),
    'thumb_store': DirectoryStore(config.THUMB_STORE_DIR),
}
routes = [
    ('/items', ItemsResource),
    ('/items/{item_id}', ItemResource),
    (('/items/{item_id}/data', '/items/{item_id}/thumb'), ItemDataResource),

    ('/items/{item_id}/tags', None),
    ('/items/{item_id}/groups', None),

    ('/tags', None),
    ('/tags/{tag_id}', None),

    ('/groups', None),
    ('/groups/{group_id}', None),
]


def add_route(path, klass):
    if klass is None:
        print("WARN: Null handler for: %s" % (path,))
    else:
        app.add_route(path, klass(**opts))

for path, klass in routes:
    if isinstance(path, (list, tuple)):
        for x in path:
            add_route(x, klass)
    else:
        add_route(path, klass)
