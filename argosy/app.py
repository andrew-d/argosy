import re
import logging
import hashlib
import datetime
from contextlib import closing

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask.ext.peewee.db import Database
from flask.ext.peewee.utils import get_object_or_404, object_list
from PIL import Image
from peewee import *

from .store import DirectoryStore


logging.basicConfig(format="%(asctime)-15s: %(message)s",
                    level=logging.DEBUG)


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('argosy.default_config')
app.config.from_pyfile('argosy.cfg', silent=True)

db = Database(app)
image_store = DirectoryStore(app.config['IMAGE_STORE_DIR'])
thumb_store = DirectoryStore(app.config['THUMB_STORE_DIR'])


# TODO: this can probably be improved
def split_tags(s):
    bits = re.findall(r'([^ \t\n\r\f\v"]+|".*?")', s)
    ret = []
    for x in bits:
        if x.startswith('"') and x.endswith('"'):
            if len(x) < 3:
                continue
            ret.append(x[1:-1])
        else:
            ret.append(x)

    return ret


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


def process_uploaded_file(uploaded_file):
    # Read file data.
    file_data = uploaded_file.read()

    # Hash the file.
    h = hashlib.sha256()
    h.update(file_data)
    file_hash = h.hexdigest()

    uploaded_file.seek(0)

    try:
        i = Item.get(Item.hash == file_hash)
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

    return i


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('upload')
        if f is None:
            abort(400)

        if not f.mimetype.startswith('image/'):
            abort(400)

        i = process_uploaded_file(f)

        # Check for tags.
        tags = request.form.get('tags')
        group = request.form.get('group')

        if tags is not None:
            for tag in split_tags(tags):
                # Create or get tag.
                try:
                    tagobj = Tag.get(Tag.name == tag)
                except Tag.DoesNotExist:
                    tagobj = Tag.create(name=tag)

                # Create or get the many-to-many relationship
                try:
                    mtm = ItemTag.get(ItemTag.item == i,
                                      ItemTag.tag == tagobj)
                except ItemTag.DoesNotExist:
                    mtm = ItemTag.create(item=i, tag=tagobj)

        if group is not None:
            # Create or get the group object.
            try:
                groupobj = Group.get(Group.name == group)
            except Group.DoesNotExist:
                groupobj = Group.create(name=group)

            # Create or get the many-to-many relationship
            try:
                mtm = ItemGroup.get(ItemGroup.item == i,
                                    ItemGroup.group == groupobj)
            except ItemGroup.DoesNotExist:
                mtm = ItemGroup.create(item=i, group=groupobj)

        resp = {
            'name': f.filename,
            'size': i.file_size,
            'url': url_for('single_item_data', id=i.hash),
            'thumbnailUrl': url_for('single_item_thumb', id=i.hash),
        }

        return jsonify(files=[resp])
    else:
        return render_template('upload.html')


@app.route('/items')
def all_items():
    items = Item.select().order_by(Item.created_on.desc())
    return object_list('items.html', items, banner='All Items')


@app.route('/items/<id>')
def single_item(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    tags = (Tag
            .select()
            .join(ItemTag)
            .join(Item)
            .where(Item.hash == item.hash))
    groups = (Group
              .select()
              .join(ItemGroup)
              .join(Item)
              .where(Item.hash == item.hash))
    return render_template('item.html',
                           item=item,
                           tags=tags,
                           groups=groups)


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


@app.route('/tags')
def tags():
    tags = Tag.select().order_by(Tag.name.asc())
    return render_template('tags.html', tags=tags)


@app.route('/tags/<int:id>')
def single_tag(id):
    tag = get_object_or_404(Tag.select(), Tag.id == id)
    items = Item.select().join(ItemTag).join(Tag).where(Tag.id == id)
    return object_list('items.html', items,
                       banner="Items with tag '%s'" % (tag.name,)
                       )


@app.route('/groups/<int:id>')
def single_group(id):
    group = get_object_or_404(Group.select(), Group.id == id)
    items = Item.select().join(ItemGroup).join(Group).where(Group.id == id)
    return object_list('items.html', items,
                       banner="Items in group '%s'" % (group.name,)
                       )


@app.route('/groups')
def groups():
    groups = Group.select().order_by(Group.name.asc())
    return render_template('groups.html', groups=groups)


@app.route('/search')
def search():
    # Parse form inputs
    allOf = request.args.get('allOf') or ''
    anyOf = request.args.get('anyOf') or ''
    noneOf = request.args.get('noneOf') or ''

    allOfL = split_tags(allOf)
    anyOfL = split_tags(anyOf)
    noneOfL = split_tags(noneOf)

    # Make sure that we have some valid query.
    if len(allOfL) + len(anyOfL) + len(noneOfL) == 0:
        return render_template('search.html')

    # SELECT *
    #   FROM Item
    #   JOIN ItemTag
    #     ON Item.hash = ItemTag.item_id
    #   JOIN Tag
    #     ON ItemTag.tag_id = Tag.id
    #  GROUP BY Item.hash
    # HAVING SUM(CASE WHEN Tag.name IN (required) THEN 1 ELSE 0 END) = N
    #    AND SUM(CASE WHEN Tag.name IN (any of  ) THEN 1 ELSE 0 END) >= 0
    #    AND SUM(CASE WHEN Tag.name IN (none of ) THEN 1 ELSE 0 END) = 0

    clauses = []
    if len(allOfL) > 0:
        clauses.append(fn.Sum(Tag.name << allOfL)  == len(allOfL))
    if len(anyOfL) > 0:
        clauses.append(fn.Sum(Tag.name << anyOfL)  >= 0)
    if len(noneOfL) > 0:
        clauses.append(fn.Sum(Tag.name << noneOfL) == 0)

    query = (Item
             .select()
             .join(ItemTag)
             .join(Tag)
             .group_by(Item.hash)
             .having(
                 *clauses
             ))

    return object_list('search.html', query,
                       allOf=allOf, anyOf=anyOf, noneOf=noneOf)


@app.route('/about')
def about():
    stats = {
        'Total Items': Item.select(fn.Count(Item)).scalar(),
        'Total Tags': Tag.select(fn.Count(Tag)).scalar(),
        'Total Groups': Group.select(fn.Count(Group)).scalar(),
    }

    return render_template('about.html', stats=stats)


@app.route('/')
def index():
    return render_template('index.html')
