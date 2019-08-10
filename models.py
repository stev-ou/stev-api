from mongoengine import Document
from mongoengine.fields import (
    FloatField, ReferenceField, StringField,
)

class Review(Document):
    meta = {'collection': 'ARC'}
    college_code = StringField()
    instructor = StringField()
    department_mean = FloatField()
