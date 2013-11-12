import re
import random
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


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('argosy.default_config')
app.config.from_envvar('ARGOSY_CONFIG', silent=True)

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


def join_tags(l):
    ret = []
    for x in l:
        # TODO: doesn't handle things with quotes
        if set(' \t\n\r\f\v') & set(x):
            ret.append('"' + x + '"')
        else:
            ret.append(x)

    return ' '.join(ret)


######################################################################
## Models

class Group(db.Model):
    id = PrimaryKeyField()
    name = CharField()


class Item(db.Model):
    # SHA-256 hash of contents of item, also PK
    hash = CharField(primary_key=True)

    # Metadata about item
    created_on = DateTimeField()
    file_size  = IntegerField()

    # Dimensions of image
    width  = IntegerField()
    height = IntegerField()

    # Whether it's an animated GIF (and thus, needs to be served as such).
    is_animated_gif = BooleanField()

    # Group (optional)
    group = ForeignKeyField(Group, null=True, related_name='items')


class Tag(db.Model):
    id = PrimaryKeyField()
    name = CharField()


class ItemTag(db.Model):
    id = PrimaryKeyField()
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
        return Item.get(Item.hash == file_hash)
    except Item.DoesNotExist:
        pass

    # Create an image from the file data.
    img = Image.open(uploaded_file)

    # See if this image is an animated GIF.
    try:
        img.seek(1)
    except EOFError:
        is_animated = False
    else:
        is_animated = True
    finally:
        img.seek(0)

    # If the image is animated, we need to save it as-is, since PIL does not
    # support writing animated GIFs.
    with closing(image_store.get_file_object(file_hash, create=True)) as new_image:
        if is_animated:
            new_image.write(file_data)
        else:
            img.save(new_image, format='PNG')

    # Create thumbnail.
    img.thumbnail((128, 128), resample=Image.ANTIALIAS)

    # Save the thumbnail.
    with closing(thumb_store.get_file_object(file_hash, create=True)) as new_thumb:
        img.save(new_thumb, format='PNG')

    i = Item(
        hash=file_hash,
        created_on=datetime.datetime.utcnow(),
        file_size=len(file_data),
        is_animated_gif=is_animated,
        width=img.size[0],
        height=img.size[1]
    )
    i.save(force_insert=True)

    return i


def update_tags(item, tags):
    for tag in tags:
        # Create or get tag.
        try:
            tagobj = Tag.get(Tag.name == tag)
        except Tag.DoesNotExist:
            tagobj = Tag.create(name=tag)

        # Create or get the many-to-many relationship
        try:
            mtm = ItemTag.get(ItemTag.item == item,
                              ItemTag.tag == tagobj)
        except ItemTag.DoesNotExist:
            mtm = ItemTag.create(item=item, tag=tagobj)


def update_group(item, group):
    # Create or get the group object.
    try:
        groupobj = Group.get(Group.name == group)
    except Group.DoesNotExist:
        groupobj = Group.create(name=group)

    # Create or get the many-to-many relationship
    item.group = groupobj
    item.save()


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('upload')
        if f is None:
            abort(400)

        # Abort early for requests that have a bad MIME type, but don't make
        # this a requirement (for example, when bulk uploading).
        if f.mimetype and not f.mimetype.startswith('image/'):
            abort(400)

        i = process_uploaded_file(f)

        # Check for tags.
        tags = request.form.get('tags')
        group = request.form.get('group')

        if tags is not None:
            update_tags(i, split_tags(tags))

        if group is not None and len(group) > 0:
            update_group(i, group)

        resp = {
            'name': f.filename,
            'size': i.file_size,
            'url': url_for('single_item', id=i.hash),
            'thumbnailUrl': url_for('single_item_thumb', id=i.hash),
        }

        return jsonify(resp)
    else:
        return render_template('upload.html')


@app.route('/items')
def all_items():
    items = Item.select().order_by(Item.created_on.desc())
    return object_list('items.html', items, banner='All Items')


# NOTE: order matters for this route, must go before single_item
@app.route('/items/untagged')
def untagged_items():
    # This does:
    #   SELECT *
    #   FROM items i
    #   LEFT JOIN itemtags t ON (i.id = t.id)
    #   WHERE t.id IS NULL
    # Effectively, we perform a left outer join, which results in NULLS for
    # fields that don't match, and then select just those items (i.e. all
    # the items with no matching ItemTag).
    untagged = Item.select().join(ItemTag, JOIN_LEFT_OUTER).where(ItemTag.id >> None)
    return object_list('items.html', untagged, banner='Untagged Items')


# NOTE: order matters for this route, must go before single_item
@app.route('/items/random')
def random_item():
    total_items = Item.select(fn.Count(Item)).order_by(Item.hash.asc()).scalar()
    item_number = random.randrange(0, total_items)

    # Get the nth item.
    item = Item.select().order_by(Item.hash.asc()).offset(item_number).limit(1).first()
    if item is None:
        raise Exception("Random item not found")
    return redirect(url_for('single_item', id=item.hash))


@app.route('/items/<id>')
def single_item(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    tags = (Tag
            .select()
            .join(ItemTag)
            .join(Item)
            .where(Item.hash == item.hash)
            .order_by(Tag.name))

    all_tags = join_tags(x.name for x in tags)

    return render_template('item.html',
                           item=item,
                           tags=tags,
                           all_tags=all_tags)


@app.route('/items/<id>/tags', methods=['POST'])
def edit_item_tags(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    tags = request.form.get('tags')
    if tags is not None:
        update_tags(item, split_tags(tags))
        flash('Tags updated successfully', 'info')
    else:
        flash('No tags given', 'warning')
    return redirect(url_for('single_item', id=id))


@app.route('/items/<id>/group', methods=['POST'])
def edit_item_group(id):
    item = get_object_or_404(Item.select(), Item.hash == id)

    group = request.form.get('group')
    if group is not None and len(group) > 0:
        update_group(group)
        flash('Group updated successfully', 'info')
    else:
        flash('No group given - nothing done', 'warning')

    return redirect(url_for('single_item', id=id))


@app.route('/items/<id>/delete', methods=['POST'])
def delete_item(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    image_store.delete(item.hash)
    thumb_store.delete(item.hash)

    # TODO: cascade delete ItemTags
    item.delete_instance()

    flash('Item was successfully deleted', 'info')
    return redirect(url_for('all_items'))


@app.route('/items/<id>/data')
def single_item_data(id):
    item = get_object_or_404(Item.select(), Item.hash == id)
    fp = image_store.get_file_object(id)
    if item.is_animated_gif:
        return send_file(fp, mimetype='image/gif')

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


@app.route('/tags/<int:id>/delete')
def delete_tag(id):
    tag = get_object_or_404(Tag.select(), Tag.id == id)
    tag.delete_instance()
    # TODO: cascade delete
    flash('Tag was successfully deleted', 'info')
    return redirect(url_for('tags'))


@app.route('/groups/<int:id>')
def single_group(id):
    group = get_object_or_404(Group.select(), Group.id == id)
    items = Item.select().join(Group).where(Group.id == id)
    return object_list('items.html', items,
                       banner="Items in group '%s'" % (group.name,)
                       )


@app.route('/tags/<int:id>/delete')
def delete_group(id):
    group = get_object_or_404(Group.select(), Group.id == id)
    group.delete_instance()
    # TODO: cascade delete
    flash('Group was successfully deleted', 'info')
    return redirect(url_for('groups'))


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
