import hashlib
import datetime
from contextlib import closing

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask.ext.peewee.db import Database
from flask.ext.peewee.utils import get_object_or_404
from PIL import Image
from peewee import *

from .store import DirectoryStore


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('argosy.default_config')
app.config.from_pyfile('argosy.cfg', silent=True)

db = Database(app)
image_store = DirectoryStore(app.config['IMAGE_STORE_DIR'])
thumb_store = DirectoryStore(app.config['THUMB_STORE_DIR'])


######################################################################
## Models

class Item(db.Model):
    # SHA-256 hash of contents of item, also PK
    hash = CharField(primary_key=True)

    # Metadata about item
    created_on = DateTimeField()
    file_size  = IntegerField()

    # Dimensions of image
    width  = IntegerField()
    height = IntegerField()

    def to_dict(self):
        return {
            'hash': self.hash,
            'created_on': self.created_on,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
        }


class Group(db.Model):
    id = PrimaryKeyField()
    name = CharField()


class ItemGroup(db.Model):
    item = ForeignKeyField(Item)
    group = ForeignKeyField(Group)


class Tag(db.Model):
    id = PrimaryKeyField()
    name = CharField()


class ItemTag(db.Model):
    item = ForeignKeyField(Item)
    tag = ForeignKeyField(Tag)


######################################################################
## Routes

def upload_file():
    uploaded_file = request.files.get('upload')
    if uploaded_file is None:
        flash('No file provided', 'danger')
        return redirect(url_for('upload'))

    if not uploaded_file.mimetype.startswith('image/'):
        flash('Invalid upload type given', 'danger')
        return redirect(url_for('upload'))

    # Read file data.
    file_data = uploaded_file.read()

    # Hash the file.
    h = hashlib.sha256()
    h.update(file_data)
    file_hash = h.hexdigest()

    uploaded_file.seek(0)

    try:
        i = Item.get(Item.hash == file_hash)
        flash('File has already been uploaded', 'warning')
    except Item.DoesNotExist:
        # Create an image from the file data.
        img = Image.open(uploaded_file)

        # Save this image to the data directory.
        with closing(image_store.get_file_object(file_hash, create=True)) as new_image:
            img.save(new_image, format='PNG')

        # Create thumbnail.
        thumb = img.resize((128, 128))

        # Save the thumbnail.
        with closing(thumb_store.get_file_object(file_hash, create=True)) as new_thumb:
            thumb.save(new_thumb, format='PNG')

        i = Item(
            hash=file_hash,
            created_on=datetime.datetime.utcnow(),
            file_size=len(file_data),
            width=img.size[0],
            height=img.size[1]
        )
        i.save(force_insert=True)
        flash('File successfully uploaded', 'success')

    return redirect(url_for('single_item', id=i.hash))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        return upload_file()
    else:
        return render_template('upload.html')


@app.route('/items/<id>')
def single_item(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    return render_template('item.html', item=item)


@app.route('/items/<id>/data')
def single_item_data(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    fp = image_store.get_file_object(id)
    return send_file(fp, mimetype='image/png')


@app.route('/items/<id>/thumb')
def single_item_thumb(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    fp = thumb_store.get_file_object(id)
    return send_file(fp, mimetype='image/png')


@app.route('/')
def index():
    return render_template('index.html')
