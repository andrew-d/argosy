#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.script import Manager
from api import app, db


manager = Manager(app)


@manager.command
def syncdb():
    """Initializes the database"""
    db.create_all()


if __name__ == "__main__":
    manager.run()
