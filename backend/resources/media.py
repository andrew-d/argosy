# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask import request, current_app, url_for, send_file
from flask.ext.restful import Resource
from ..models import *
from ..storage import FileNotFoundException


class MediaResource(Resource):
    def get(self, media_id):
        # Load this media object.
        media = Media.query.filter_by(id=media_id).first()
        if not media:
            return {
                "error": "Media file with ID '%s' not found" % (media_id,)
            }, 404

        try:
            f = current_app.store.get(media_id)
        except FileNotFoundException:
            # This should not happen!
            return {
                "error": "Media file with ID '%s' not found" % (media_id,)
            }, 404

        return send_file(f, mimetype=media.mime)


class MediaUploadResource(Resource):
    def post(self):
        # The media file should be uploaded with the form name 'media'.
        if not 'media' in request.files:
            return {
                'error': 'No uploaded file provided (are you using the '
                         '"media" form-field?)'
            }, 400

        # Get the file.
        file = request.files['media']

        # Get other information.
        tags = request.form.get('tags')
        group = request.form.get('group')

        # Depending on the mimetype...
        mime = file.mimetype.lower()
        if mime.startswith('image/'):
            ret = {'type': 'image'}
        elif mime == 'text/plain':
            ret = {'type': 'plain text'}
        elif mime == 'text/x-markdown':
            ret = {'type': 'markdown'}
        else:
            return {'type': 'unknown'}, 400

        # Ok, got a valid type.  Save it.
        key = current_app.store.save_new(file.stream.read())

        # Create a new media entry.
        media = Media(key)
        media.mime = mime

        # TODO: set tags/group
        db.session.add(media)
        db.session.commit()

        # Add a link to our return value.
        ret['url'] = url_for('media_endpoint', media_id=key)

        # Return success!
        return ret
