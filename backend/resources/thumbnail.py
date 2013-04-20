# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask import make_response
from flask.ext.restful import Resource
from ..models import *


class ThumbnailResource(Resource):
    """
    This class lets you get a thumbnail for a resource.
    """

    def get(self, media_id):
        resp = make_response('thumbnail')
        resp.headers['Content-Type'] = 'application/octet-stream'
        return resp
