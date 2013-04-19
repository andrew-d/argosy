# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

import types
import pkgutil
from flask.ext.restful import Resource

# Find all modules in this directory and save all Resources that we find.
resources = []
prefix = __name__ + "."
for importer, modname, ispkg in pkgutil.iter_modules(__path__, prefix):
    curr = __import__(modname, fromlist="dummy")

    for attr in dir(curr):
        val = getattr(curr, attr)

        # We only consider resources that are:
        #   1. A type or class
        #   2. A subclass of the Resource type
        #   3. Not the Resource type itself.
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
