from peewee import *

db = SqliteDatabase('identifier.sqlite')

class User(Model):
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    subscribed_disciplines = CharField()

    class Meta:
        database = db

class HelpRequest(Model):
    user_id = IntegerField()
    discipline = CharField()
    request_link = CharField()
    anonymous = BooleanField()

    class Meta:
        database = db

db.connect()
db.create_tables([User, HelpRequest])
