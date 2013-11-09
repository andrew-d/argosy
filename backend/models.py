import peewee
from peewee import *
from playhouse.proxy import Proxy


database_proxy = Proxy()


class ArgosyModel(Model):
    class Meta:
        database = database_proxy


class Item(ArgosyModel):
    # SHA-256 hash of contents of item, also PK
    hash = CharField(primary_key=True)

    # Metadata about item
    created_on = DateTimeField()
    file_size  = IntegerField()

    # Dimensions of image
    width  = IntegerField()
    height = IntegerField()

    def to_dict(self):
        return {
            'hash': self.hash,
            'created_on': self.created_on,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
        }


class Group(ArgosyModel):
    id = PrimaryKeyField()
    name = CharField()


class ItemGroup(ArgosyModel):
    item = ForeignKeyField(Item)
    group = ForeignKeyField(Group)


class Tag(ArgosyModel):
    id = PrimaryKeyField()
    name = CharField()


class ItemTag(ArgosyModel):
    item = ForeignKeyField(Item)
    tag = ForeignKeyField(Tag)


ALL_MODELS = (Item, Group, ItemGroup, Tag, ItemTag)


def bind_db(db):
    database_proxy.initialize(db)
    return database_proxy


def create_tables():
    peewee.create_model_tables(ALL_MODELS)


def drop_tables():
    peewee.drop_model_tables(ALL_MODELS)
