# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.restful import Resource
from ..models import *


class IndexResource(Resource):
    def get(self):
        return {'hello': 'asdf'}
