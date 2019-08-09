from mongoengine import Document
from mongoengine.fields import (
    FloatField, ReferenceField, StringField,
)


class Course(Document):
    meta = {'collection': 'department'}
    name = StringField()
    instructor = ReferenceField(Instructor)
    rating = FloatField()


class Instructor(Document):
    meta = {'collection': 'role'}
    name = StringField()
    rating = FloatField()
