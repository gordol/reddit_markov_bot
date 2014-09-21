from mongoengine import *

connect('trollolol')

class Node(Document):
    node_id   = StringField(unique = True, required = True)
    parent_id = StringField()
    body      = StringField(required = True)
    created   = IntField()
    username  = StringField()

    def __unicode__(self):
        return body
