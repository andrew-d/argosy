#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os
import sys
import datetime

import baker

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import backend

from backend.models import *
from backend import config


bind_db(config.get_db())



@baker.command
def syncdb():
    print("Synchronizing database...", end='')
    try:
        drop_tables()
    except Exception as e:
        print("Error while dropping: %s" % (e,))
    create_tables()
    print(" done!")


@baker.command
def run(port=8000):
    from backend.app import app
    from werkzeug.serving import run_simple

    host = '127.0.0.1'
    try:
        run_simple(host, port, app)
    except KeyboardInterrupt:
        print('')


if __name__ == "__main__":
    baker.run()
