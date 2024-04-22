from peewee import *

db = SqliteDatabase('identifier.sqlite')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    subscribed_disciplines = CharField()

class HelpRequest(BaseModel):
    user_id = IntegerField()
    discipline = CharField()
    request_link = CharField()
    anonymous = BooleanField()

db.connect()
db.create_tables([User, HelpRequest])