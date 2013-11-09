from __future__ import absolute_import

import re
import json
import calendar
import datetime
import falcon

from . import config


def _default_encoder(obj):
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()

        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis

    else:
        raise TypeError(
            'Object of type %s with value of %s is not JSON serializable' % (
                type(obj), repr(obj)
            ))


if config.DEBUG:
    def dumps(d):
        s = json.dumps(d, indent=2, sort_keys=True, default=_default_encoder) + '\n'
        return json_escape(s)
else:
    def dumps(d):
        return json_escape(json.dumps(d, default=_default_encoder))

def loads(s):
    try:
        return json.loads(s)
    except ValueError:
        raise falcon.HTTPBadRequest('Invalid JSON',
                                    'Invalid JSON provided')


ESCAPE_RE = re.compile(r'[<>/]')
def _escape_func(matchobj):
    ch = ord(matchobj.group(0))
    return '\\u%04x' % (ch,)

def json_escape(s):
    return ESCAPE_RE.sub(_escape_func, s)
