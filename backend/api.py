#!/usr/bin/env python

import os
from flask import Flask
from flask.ext.restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy

# Create app and configure.  Note: order matters - default comes first.
app = Flask(__name__)
app.config.from_pyfile('argosy.default_settings')
if 'ARGOSY_SETTINGS' in os.environ:
    app.config.from_envvar('ARGOSY_SETTINGS')

# Create DB and API resource.
db = SQLAlchemy(app)
api = Api(app)


class MediaType(db.Model):
    __tablename__ = 'mediatypes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<MediaType %r>" % (self.name,)


class Media(db.Model):
    __tablename__ = 'media'

    # Media is indexed by the SHA-256 hash of its contents.
    id = db.Column(db.String(32), primary_key=True)

    type_id = db.Column(db.Integer, db.ForeignKey('mediatypes.id'), nullable=False)
    type = db.relationship('MediaType',
                           backref=db.backref('media', lazy='dynamic'))

    # Tags and groups use the Tables below.
    tags = db.relationship("Tag", secondary=media_tags,
                        backref=db.backref("media", lazy="dynamic")
                        )

    groups = db.relationship("MediaGroup", secondary=media_groups,
                          backref=db.backref("media", lazy="dynamic")
                          )


    def __repr__(self):
        return "<Media %d, type: %s>" % (self.id, self.type.name)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag %s>" % (self.name,)


class TagAlias(db.Model):
    __tablename__ = 'tagaliases'

    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))

    tag = db.relationship("Tag", backref=db.backref("aliases", lazy="dynamic"))

    def __init__(self, alias, tag):
        self.alias = alias
        self.tag = tag

    def __repr__(self):
        return "<TagAlias %s -> %s>" % (self.alias, self.tag.name)


class MediaGroup(db.Model):
    __tablename__ = 'mediagroups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<MediaGroup %s>" % (self.name,)


# Table for the many-to-many relationship between media and tags.
media_tags = db.Table("media_tags",
                  db.Column("media_key", db.String, db.ForeignKey("media.id")),
                  db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
                  )


# Table for the many-to-many relationship between media and groups.
media_groups = db.Table("media_groups",
                    db.Column("media_key", db.String, db.ForeignKey("media.id")),
                    db.Column("group_id", db.Integer, db.ForeignKey("mediagroups.id"))
                    )



class HelloWorld(Resource):
    def get(self):
        return {'hello': 'asdf'}


api.add_resource(HelloWorld, '/')


if __name__ == '__main__':
    app.run(debug=True)
