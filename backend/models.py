# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division, with_statement

from flask.ext.sqlalchemy import SQLAlchemy

# Create the database (but don't bind it yet.
db = SQLAlchemy()

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

    def __init__(self, alias, tag_id):
        self.alias = alias
        self.tag_id = tag_id

    def __repr__(self):
        if self.tag is not None:
            return "<TagAlias '%s' -> '%s'>" % (self.alias, self.tag.name)
        else:
            return "<TagAlias '%s' -> %d>" % (self.alias, self.tag_id)


class MediaGroup(db.Model):
    __tablename__ = 'mediagroups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<MediaGroup %s>" % (self.name,)
