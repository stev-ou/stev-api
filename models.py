from mongoengine import Document
from mongoengine.fields import (
    FloatField, StringField, IntField
)
from constants import DB_NAME, COLLECTION_NAME, AGGREGATED_COLLECTION_NAME

def declare_fields(float_fields, string_fields, int_fields):
    """
    Takes three lists of strings denoting fields with type float, string, or int, and converts them
    """
    floats = [FloatField(name=i) for i in float_fields]
    strings = [StringField(name=i) for i in string_fields]
    ints = [IntField(name=i) for i in int_fields]
    return floats, strings, ints

class Review(Document):
    meta = {'collection': COLLECTION_NAME}
    # # Define the types for each field
    # float_fields = ['Mean', 'Standard Deviation']
    # string_fields = ['College Code', 'Instructor First Name', 'Instructor Last Name', 'Question', \
    #     'Section Title', 'Subject Code', 'course_uuid']
    # int_fields = ['Course Number', 'Responses', 'Question Number', 'Term Code', 'Instructor ID']
    # f,s,i = declare_fields(float_fields, string_fields, int_fields)
    # mean=FloatField(name='Mean')
    college_code = StringField(name="College Code", help_text="The \
        abbreviated name of the college ")
    course_number = IntField(name="Course Number")
    instructor_first_name = StringField(name="Instructor First Name")
    instructor_id = IntField(name="Instructor ID")
    instructor_last_name = StringField(name="Instructor Last Name")
    mean = FloatField(name="Mean")
    question = StringField(name="Question")
    question_number = IntField(name="Question Number")
    section_number = IntField(name="Section Number")
    section_title = StringField(name="Section Title")
    standard_deviation = FloatField(name="Standard Deviation")
    subject_code = StringField(name="Subject Code")
    term_code = IntField(name="Term Code")
    responses = IntField(name="Responses")

class AggregatedReviews(Document):
    meta = {'collection': AGGREGATED_COLLECTION_NAME}
    # All features
    # 'Course Title',    
    # Define the types for each field
    # float_fields = ['Avg Instructor Rating In Section', 'SD Instructor Rating In Section', 'Avg Course Rating', 'SD Course Rating', \
    #     'Avg Department Rating', 'SD Department Rating', 'Course Rank in Department in Semester']
    # string_fields = ['College Code', 'Instructor First Name', 'Instructor Last Name', 'Question', \
    #     'Course Title', 'Subject Code', 'course_uuid']
    # int_fields = ['Course Number', 'Responses', 'Term Code', 'Instructor ID', 'Instructor Enrollment', 'Course Enrollment', ]
    # f,s,i = declare_fields(float_fields, string_fields, int_fields)
    # Above lines wont work and I dont entirely understand why

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
