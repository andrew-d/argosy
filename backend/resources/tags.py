# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.restful import Resource, reqparse
from ..models import *


tags_post_parser = reqparse.RequestParser()
tags_post_parser.add_argument('tag', type=str, required=True, help='Tag cannot be blank!')

tags_get_parser = reqparse.RequestParser()
tags_get_parser.add_argument('page', type=int, help='Page could not be converted')

class TagsResource(Resource):
    """
    This class lets you add a new tag.
    """
    def get(self):
        args = tags_get_parser.parse_args()

        # Create a query for all tags.
        tags = Tag.query.paginate(args['page'] or 1, error_out=False).items
        return {
            "tags": [
                t.name for t in tags
            ]
        }

    def post(self):
        args = tags_post_parser.parse_args()

        # See if this tag exists.
        tag = Tag.query.filter_by(name=args['tag']).first()
        if tag:
            return {"error": "The tag '%s' already exists!" % (tag.name,)}, 409

        # See if the tag alias already exists.
        alias = TagAlias.query.filter_by(alias=args['tag']).first()
        if alias:
            return {
                "error": "Cannot create tag; the alias '%s' for tag '%s' "
                          "already exists!" % (args['tag'], alias.tag.name)
            }, 409

        # Create it.
        new_tag = Tag(args['tag'])
        db.session.add(new_tag)
        db.session.commit()

        return {"created": True}
