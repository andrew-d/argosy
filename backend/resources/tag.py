# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.restful import Resource, reqparse
from ..models import *


tag_parser = reqparse.RequestParser()
tag_parser.add_argument('page', type=int, help='Page cannot be converted')

class TagResource(Resource):
    """
    This class lets you get or delete a specific tag.
    """

    def get(self, tag_id):
        # Parse arguments.
        args = tag_parser.parse_args()
        page = args['page'] or 1

        # Try and find an alias.
        tag = tag_id
        alias = TagAlias.query.filter_by(alias=tag).first()
        if alias:
            tag = alias.tag

        # Get from database.
        # tags = s

        return {"tag": tag, 'page': page}

    def delete(self, tag_id):
        return {"deleting": True}
