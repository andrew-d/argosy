# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.restful import Resource
from ..models import *


class MediaResource(Resource):
    def get(self, media_id):
        print("Getting ID:", media_id)
        return {"media": "foo"}

    def post(self):
        print('Uploaded files: ' + repr(request.files))
        return {'foo': 'bar'}



