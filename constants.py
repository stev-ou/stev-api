# Current working name of the database, collections, etc.
DB_NAME = "reviews-db-v1"
COLLECTION_NAME = "reviews"
AGGREGATED_COLLECTION_NAME='aggregated_reviews'
OCR_DB_NAME = 'ocr_db_v1'

# The term code dict maps the term code (6 digit code) to a more readable format (e.g., Spring 2017)
SEMESTER_MAPPINGS= {'201010': 'Fall 2010',
    '201020': 'Spring 2010',
    '201030': 'Summer 2010',
    '201110': 'Fall 2011',
    '201120': 'Spring 2011',
    '201130': 'Summer 2011',
    '201210': 'Fall 2012',
    '201220': 'Spring 2012',
    '201230': 'Summer 2012',
    '201310': 'Fall 2013',
    '201320': 'Spring 2013',
    '201330': 'Summer 2013',
    '201410': 'Fall 2014',
    '201420': 'Spring 2014',
    '201430': 'Summer 2014',
    '201510': 'Fall 2015',
    '201520': 'Spring 2015',
    '201530': 'Summer 2015',
    '201610': 'Fall 2016',
    '201620': 'Spring 2016',
    '201630': 'Summer 2016',
    '201710': 'Fall 2017',
    '201720': 'Spring 2017',
    '201730': 'Summer 2017',
    '201810': 'Fall 2018',
    '201820': 'Spring 2018',
    '201830': 'Summer 2018',
    '201910': 'Fall 2019',
    '201920': 'Spring 2019',
    '201930': 'Summer 2019',
    '202010': 'Fall 2020',
    '202020': 'Spring 2020',
    '202030': 'Summer 2020',
    '202110': 'Fall 2021',
    '202120': 'Spring 2021',
    '202130': 'Summer 2021',
    '202210': 'Fall 2022',
    '202220': 'Spring 2022',
    '202230': 'Summer 2022',
    '202310': 'Fall 2023',
    '202320': 'Spring 2023',
    '202330': 'Summer 2023'} 

# These map the headers in the college to the short names in the db. 
# Note that short names are just first char of each word in the College Name, w/o spaces.
header_col_mapper: {'College of Architecture': 'CoA',
'College of Arts and Sciences': 'CoAaS',
'College of Atmospheric & Geographic Sciences': 'CoA&GS',
'College of Continuing Education - Department of Aviation': 'CoCE-DoA',
'Michael F. Price College of Business': 'MFPCoB',
'Melbourne College of Earth and Energy': 'MCoEaE',
'Jeannine Rainbolt College of Education': 'JRCoE',
'Gallogly College of Engineering': 'GCoE',
'Weitzenhoffer Family College of Fine Arts': 'WFCoFA',
'Honors College': 'HC', 'College of International Studies': 'CoIS',
'Gaylord College of Journalism and Mass Communication': 'GCoJaMC',
'College of Professional and Continuing Studies': 'CoPaCS',
'University College': 'UC', 'Center for Independent and Distance Learning': 'CfIaDL',
'Expository Writing Program': 'EWP', 'ROTC - Air Force': 'R-AF'}

# DEPRECATED
# Builds necessary dictionaries to allow mapping of values from the output data to courses, instructors, etc.
# Build a dict mapping Colleges to Question numbers to weight if thats something we pursue. See example below. Used in data agg for weighting questions.
# Instructor_question_weighting:
#     GCoE:
#         '2': 1
#         '3': 1
#         '4': 1
#         '5': 1
#         '6': 1
#         '7': 1
#         '10': 1
#         '16': 1
#         '27': 1
#         '33': 1

# This dictionary below shows the desired output mappings for each column in aggregated data, alongside a brief description
# Ag_df_indices:{0: 'Term Code',
# 1: 'College Code', etc.}

# I don't think we will need to use the below dictionary
# Department_code_dict: {'EN00': 'ENGR', 'EN01': 'AME', 'EN02': 'CH E', 'EN03':'CEES'}