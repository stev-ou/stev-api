from mongoengine import Document
from mongoengine.fields import (
    FloatField, StringField, IntField
)

class Review(Document):
    meta = {'collection': 'ARC'}
    college_code = StringField()
    instructor = StringField()
    department_mean = FloatField()

class AggReview(Document):
    meta = {'collection': 'aggregated_ARC'}
    college_code = StringField()
    instructor_id = IntField()
    avg_dept_rating = FloatField()
