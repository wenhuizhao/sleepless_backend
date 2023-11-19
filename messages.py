
from mongoengine.document import Document
from mongoengine.fields import EmailField, ImageField, IntField, StringField, UUIDField

# inheriting from Document class
class Message(Document):
    meta = {"collection": "Message"}
    uuid=UUIDField()
    text=StringField(required=True)
    author=StringField(required=True)

  
