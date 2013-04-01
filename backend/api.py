# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

import os
import sys
from flask import Flask, request
from flask.ext.restful import Api

from .middleware import MethodRewriteMiddleware
from .models import *
from .resources.all import *

from . import default_settings


# Create app and configure.  Note: order matters - default comes first.
app = Flask(__name__)
app.config.from_object(default_settings)
if 'ARGOSY_SETTINGS' in os.environ:
    app.config.from_envvar('ARGOSY_SETTINGS')

# Create DB and API resource.
db.init_app(app)
api = Api(app)

# Add middleware.
app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)

# Set up routes.
api.add_resource(IndexResource, '/')
api.add_resource(MediaResource, '/media/<string:media_id>')
api.add_resource(ThumbnailResource, '/thumbnails/<string:media_id>')
api.add_resource(TagsResource, '/tags/')
api.add_resource(TagResource, '/tags/<string:tag_id>')
api.add_resource(TagAliasesResource, '/aliases/')
api.add_resource(TagAliasResource, '/aliases/<string:alias_id>')


@app.after_request
def allow_cors(response):
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With'
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response
