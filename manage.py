#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os
import sys
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
    try:
        for model in models:
            model.drop_table()
            model.create_table()
    except Exception as e:
        print("Error while creating: %s" % (e,))
    print(" done!")


@baker.command
def run(port=8000):
    try:
        app.run(port=port)
    except KeyboardInterrupt:
        print('')


if __name__ == "__main__":
    baker.run()
