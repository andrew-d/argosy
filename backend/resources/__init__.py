# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

import types
import pkgutil
from flask.ext.restful import Resource

# from .tag import TagResource
# from .tags import TagsResource
# from .media import MediaResource
# from .thumbnail import ThumbnailResource
# from .tagalias import TagAliasResource
# from .index import IndexResource

# Find all modules in this directory and save all Resources that we find.
resources = []
prefix = __name__ + "."
for importer, modname, ispkg in pkgutil.iter_modules(__path__, prefix):
    curr = __import__(modname, fromlist="dummy")

    for attr in dir(curr):
        val = getattr(curr, attr)
        if (isinstance(val, (type, types.ClassType)) and
            issubclass(val, Resource) and val is not Resource):
            resources.append(val)

# Set all the resources as attributes on our dummy module.
from . import all as all_mod
for res in resources:
    name = res.__name__

    existing = getattr(all_mod, name, None)
    if existing is not None:
        raise RuntimeError("Resource with name %s is defined twice: %r and "
                           "%r" % (name, existing, res))

    setattr(all_mod, name, res)
