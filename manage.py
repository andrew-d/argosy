#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os
import sys
import requests
import datetime

import baker

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import argosy
from argosy.app import app, db


@baker.command
def syncdb():
    # Find all models.
    models = []
    for attr in dir(argosy.app):
        item = getattr(argosy.app, attr)
        if isinstance(item, type) and issubclass(item, db.Model):
            models.append(item)
    print("Found %d models" % (len(models),))

    print("Synchronizing database...", end='')
    for model in models:
        # Ignore errors while dropping...
        try:
            model.drop_table()
        except Exception:
            pass

        # ... but report them while creating.
        try:
            model.create_table()
        except Exception as e:
            print("Error while creating %s: %s" % (
                model.__name__, e))
            break

    print(" done!")


@baker.command
def run(port=8000):
    try:
        app.run(port=port)
    except KeyboardInterrupt:
        print('')


VALID_EXTS = set(['.png', '.gif', '.jpg', '.jpeg'])
def is_image_file(name):
    _, ext = os.path.splitext(name)
    return ext.lower() in VALID_EXTS


def do_import(file_path, server, tags, group):
    url = 'http://%s/upload' % (server,)
    files = {'upload': open(file_path, 'rb')}
    data = {}

    if tags is not None and len(tags) > 0:
        data['tags'] = tags
    if group is not None and len(group) > 0:
        data['group'] = group

    r = requests.post(url, files=files, data=data)
    if r.ok:
        print("[OK] %s" % (file_path,))
    else:
        print("[FAIL] %s" % (file_path,))


@baker.command
def bulk_import(dir, recursive=False,
                tags=None, group=None,
                host='localhost', port=8000,
                ):
    from_dir = os.path.abspath(dir)
    remote = '%s:%d' % (host, port)

    print("Importing from directory: %s" % (from_dir,))
    if not recursive:
        for f in os.listdir(from_dir):
            if is_image_file(f):
                do_import(
                    os.path.join(from_dir, f),
                    remote,
                    tags,
                    group
                )
    else:
        for root, dirs, files in os.walk(from_dir):
            for f in files:
                if is_image_file(f):
                    do_import(
                        os.path.join(from_dir, root, f),
                        remote,
                        tags,
                        group
                    )


if __name__ == "__main__":
    baker.run()
