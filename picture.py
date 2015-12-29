from datetime import datetime

from couchdb.mapping import Document, TextField, IntegerField, DateTimeField


class Picture(Document):
    name = TextField()
    width = IntegerField()
    height = IntegerField()
    mime_type = TextField()
    size = IntegerField()
    phash = TextField()
    created = DateTimeField(default=datetime.now)
