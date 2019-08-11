from mongoengine import Document
from mongoengine.fields import (
    FloatField, StringField, IntField
)

class Review(Document):
    meta = {'collection': 'ARC'}
    college_code = StringField(name="College Code")
    college_mean = FloatField(name="College Mean")
    college_median = FloatField(name="College Median")
    course_number = IntField(name="Course Number")
    department_mean = FloatField(name="Department Mean")
    department_median = IntField(name="Department Median")
    department_responses = IntField(name="Department Responses")
    department_std_dev = FloatField(name="Department Standard Deviation")
    individual_responses = IntField(name="Individual Responses")
    instructor_first_name = StringField(name="Instructor First Name")
    instructor_id = IntField(name="Instructor ID")
    instructor_last_name = StringField(name="Instructor Last Name")
    mean = FloatField(name="Mean")
    median = IntField(name="Median")
    percent_rank_college = FloatField(name="Percent Rank - College")
    percent_rank_department = FloatField(name="Percent Rank - Department")
    question = StringField(name="Question")
    question_number = IntField(name="Question Number")
    section_number = IntField(name="Section Number")
    section_title = StringField(name="Section Title")
    standard_deviation = FloatField(name="Standard Deviation")
    subject_code = StringField(name="Subject Code")
    term_code = IntField(name="Term Code")
    responses = IntField(name="Responses")

class AggReview(Document):
    meta = {'collection': 'aggregated_INTS'}
    college_code = StringField(name="College Code")
    instructor_id = IntField(name="Instructor ID")
    avg_course_rating = FloatField(name="Avg Course Rating")
