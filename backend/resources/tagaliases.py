# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.restful import Resource, reqparse
from ..models import *


tag_alias_parser = reqparse.RequestParser()
tag_alias_parser.add_argument('alias', type=str, required=True,
                             help='Alias cannot be blank!')
tag_alias_parser.add_argument('tag', type=str, required=True,
                             help='Tag cannot be blank!')

class TagAliasesResource(Resource):
    """
    This resource lets you list all tag aliases, or add a new one.
    """
    def get(self):
        aliases = TagAlias.query.all()

        return {
            "aliases": [
                {"tag": a.tag.name, "alias": a.alias} for a in aliases
            ]
        }

    def post(self):
        args = tag_alias_parser.parse_args()

        # Look up a tag with this ID.
        dest_tag = Tag.query.filter(Tag.name == args['tag']).first()

        # Create a new alias.
        if not dest_tag:
            return {"error": "The tag '%s' does not exist!" % (args['tag'],)}, 404

        alias = TagAlias(args['alias'], dest_tag.id)
        db.session.add(alias)
        db.session.commit()

        return {"created": True}
