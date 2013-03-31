# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.restful import Resource, reqparse
from ..models import *


class TagAliasResource(Resource):
    """
    This resource lets you view information about or delete a specified tag
    alias.
    """
    def get(self, alias_id):
        a = TagAlias.query.filter_by(alias=alias_id).first()
        if a is None:
            return {"error": "Alias '%s' does not exist" % (alias_id,)}
        else:
            return {"tag": a.tag.name, "alias": a.alias}

    def delete(self, alias_id):
        # TODO
        return {"deleted": True}
