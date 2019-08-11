from mongoengine import Document
from mongoengine.fields import (
    FloatField, StringField, IntField
)

class Review(Document):
    meta = {'collection': 'ARC'}
    college_code = StringField(name="College Code", help_text="The \
        abbreviated name of the college ")
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

class AggregatedReviews(Document):
    meta = {'collection': 'aggregated_ARC'}
    college_code = StringField(name="College Code")
    course_number = IntField(name="Course Number")
    instructor_enrollment = IntField(name="Instructor Enrollment")
    avg_department_rating = FloatField(name="Avg Department Rating")
    sd_department_rating = FloatField(name="SD Department Rating")
    instructor_first_name = StringField(name="Instructor First Name")
    instructor_id = IntField(name="Instructor ID")
    avg_course_rating = FloatField(name="Avg Course Rating")
    sd_course_rating = FloatField(name="SD Course Rating")
    course_rank_in_dept_in_sem = IntField(name="Course Rank in Department in Semester")
    instructor_last_name = StringField(name="Instructor Last Name")
    course_title = StringField(name="Course Title")
    avg_instructor_rating_in_sec = FloatField(name="Avg Instructor Rating In Section")
    sd_instructor_rating_in_sec = FloatField(name="SD Instructor Rating In Section")
    subject_code = StringField(name="Subject Code")
    course_enrollment = IntField(name="Course Enrollment")
    term_code = IntField(name="Term Code")
    course_uuid = StringField(name="course_uuid")
