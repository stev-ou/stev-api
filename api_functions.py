import pprint
import json
from mongo import mongo_driver
import pandas as pd
from collections import Counter
import re
import os
import yaml
import pymongo
import numpy as np
from datetime import datetime

# Establish the DB Name 
DB_NAME = "reviews-db-v1"

# This is the set of that will be queried by the API
# The order is important, collections are searched in this order
COLLECTION_NAMES = ['reviews'] #,'JRCOE', 'COAS', 'ARC', 'BUS', 'FARTS', 'GEO', 'INTS', 'JRNL', 'NRG']
AGG_COLLECTION_NAMES = ["aggregated_"+ name for name in COLLECTION_NAMES]

# This is the period that will be considered "current" by the API. 
# These are term codes, where the first 4 digits corresponds to year, last 2 digits to semester (10:fall, 20:spring, 30:summer), 
# e.g. 201710 is Fall 2017
CURRENT_SEMESTERS = [201920, 201810, 201820, 201830, 201710, 201720, 201730, 201610 ]

# Import the mappings to find the semester for each course
# Read in the question mappings values from the mappings.yaml
# Get file location for mappings.yaml and reading data
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
file_path = __location__+"/mappings.yaml"

with open(file_path) as f:
    # use safe_load instead load
    mappings = yaml.safe_load(f)
    SEMESTER_MAPPINGS = mappings['Term_code_dict']

# Sort by term code
def sort_by_term_code(semester_int_list):
    """
    Input a list of term codes, it will sort the term code list and return the same list sorted in order of term.
    """
    year_list = [int(str(i)[0:4]) for i in semester_int_list]
    year_list.sort(reverse=True)
    final_order = []
    for year in year_list:
        # Find the semesters of the year
        sems = [sem for sem in semester_int_list if str(sem)[0:4] == str(year)]
        for ending in ['10', '30', '20']:
            for sem in sems:
                if str(sem)[-2:] == ending and sem not in final_order:
                    final_order.append(sem)
    if set(final_order)!=set(semester_int_list):
        raise Exception('Sorting term codes didnt work in the api generator')
    return final_order# return the most recent sem as a term code

# Get the collection of interest from the db, based on a filter and potentially a known collection
def query_df_from_mongo(db,coll_filter, collections = AGG_COLLECTION_NAMES):
    """
    This function will use a coll_filter, AKA a cursor, to query the collections in COLLECTION_NAMES and will then return 
    the db and the coll_name where the filter was found.
    Inputs:
    db - a connection to the mongodb, or more concretely a mongo_driver() object
    coll_filter - a valid filter of the form required by mongodb
    collections (optional) - a list of collections to search through for the cursor/filter

    Returns:
    db - a pd DataFrame containing the results of the query
    coll_name - the collection name (str) where the coll_filter was found
    """
    for coll_name in collections:
        coll = db.get_db_collection(DB_NAME, coll_name)
        # Use the database query to pull needed data
        cursor = coll.find(coll_filter)
        # For whatever reason, generating a dataframe clears the cursor, so get population here
        population = coll.count_documents(coll_filter)
        # This assumes that there will be no same uuid's across the different collections, e.g. the same uuid in GCOE and JRCOE
        if population > 0:
            df = pd.DataFrame(list(cursor))
            break

    # Add an error catching if the len(df) == 0
    if population==0:
        print('The below filter was not found within any of the mongo collection.')
        pprint.pprint(coll_filter)
        raise Exception('The filter was not found in the mongo collection.')
    return df, coll_name

def drop_duplicate_courses(df):
    # Get the list of the most popular Course Titles of this course, and trim any entries that arent the most popular course name
    if 'Section Title' in df.columns:
        most_frequent_course = df['Section Title'].value_counts().idxmax()
        df.drop(df[(df['Section Title']!=most_frequent_course)].index, inplace=True)
    elif 'Course Title' in df.columns:
        most_frequent_course = df['Course Title'].value_counts().idxmax()
        df.drop(df[(df['Course Title']!=most_frequent_course)].index, inplace=True)
    return


###### APIs for Searchby course ########

def CourseFig1Table(db, uuid):
    '''
    This function will take one validated course-based uuid in the aggregated database and will
    build a json response to present the values needed for figure 1. Briefly, this api response 
    will show all of the professors who have taught the course in the most recent semester, what
    rating each professor received, and what average rating each instructor received on average 
    in the most recent semester of data.
    api schema defined in api_schema.py
    Inputs: db - a connection to the mongodb, i.e. db = mongo_driver()
            valid_uuid - a validated uuid from the 'uuid' field in the dataframe
    Returns: a valid json needed to generate the figure
    '''
    # Construct the json containing necessary data for figure 1 on course page
    ret_json = {"result": {"instructors": []}}

    # filter that we use on the collection
    coll_filter = {'$and':[
            {"course_uuid":uuid},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter)
    drop_duplicate_courses(df)

    # The following is a very crappy way to get a list of unique indices that are in the order of the semesters
    #######
    # Define the instructor list
    instructor_list = list(df.drop_duplicates('Instructor ID', inplace=False)['Instructor ID'])
    term_code_list = list(df.drop_duplicates(['Instructor ID','Term Code'], inplace=False)['Term Code'])

    # Sort the term code list using prebuilt function
    term_code_list = sort_by_term_code(term_code_list)

    # Create the dict for this sorted term code list
    dict_term_list = {k: v for v, k in enumerate(term_code_list)}

    # Add the column as a mapping to the df
    df['sorter'] = df['Term Code']

    df['sorter'].replace(dict_term_list, inplace=True)
    df.sort_values('sorter', inplace=True)
    instructor_list = list(df.drop_duplicates('Instructor ID', inplace=False)['Instructor ID'])

    # Get the large df with all of the instructors
    coll_filter = {'$and':[
    {"Instructor ID":{'$in':instructor_list}},
    {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df_main, coll_name = query_df_from_mongo(db, coll_filter, collections = [coll_name])

    for inst_id in instructor_list:
        # need to average all ratings across all classes taught by each instructor

        df_inst = df_main[(df_main['Instructor ID']==inst_id)] # Made df_inst once and then slice it for each instructor

        avg = df_inst['Avg Instructor Rating In Section'].mean()

        # Define a list of the term codes this instructor has taught
        term_code_list = df_inst[df_inst['course_uuid']==uuid]['Term Code']
        term_code_list = sort_by_term_code(term_code_list)
        term_code_list = [SEMESTER_MAPPINGS[str(i)] for i in term_code_list]
        terms_taught = ''
        for j in term_code_list:
            terms_taught += j
            if j != term_code_list[-1]:
                terms_taught+=', '
            else:
                break

        inst = {
            "name": str(df_inst["Instructor First Name"].unique()[0] + ' ' + df_inst['Instructor Last Name'].unique()[0]),
            "crs rating": df[df['Instructor ID']==inst_id]['Avg Instructor Rating In Section'].mean(),
            "avg rating": avg,
            "term": terms_taught
            }

        ret_json["result"]["instructors"].append(inst)

    # grabs the first row with .iloc[0]
    ret_json['result']['course name'] = str(df['Course Title'].iloc[0])
    ret_json['result']['dept name'] = str(df['Subject Code'].iloc[0])
    ret_json['result']['course number'] = str(df['Course Number'].iloc[0])
                
    return ret_json

def CourseFig2Chart(db, valid_uuid):
    '''
    This function will build the json for the response to build the relative department rating figure 
    (2nd from top on the left side). The json has structure given in schema.json, for this rating.

    Inputs: db - a connection to the mongodb, i.e. db=mongo_driver()
            valid_uuid - a validated uuid from the 'uuid' field in the dataframe
    Returns: a valid json needed to generate the figure
    '''
    ##### Initial setup stuff
    # Define an instructor function to return the instructor dict based on passed parameters
    def instructor(last_name, first_name, mean_in_course, semester_taught, enrollment):
        return {'name':str(last_name)+' '+str(first_name), 'instructor mean in course':float(mean_in_course), 
                'semester':str(semester_taught), 'enrollment':int(enrollment)}

    # Define a cursor with which to query mongo
    cursor = {'$and':[
    {"course_uuid":valid_uuid},
    {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    uuid_df, coll_name = query_df_from_mongo(db, cursor)
    drop_duplicate_courses(uuid_df)

    # Make sure that the df is unique wrt Term Code and instructor
    uuid_df.drop_duplicates(subset=['Term Code', 'Instructor ID'], inplace=True)

    # Start by finding the most recent appearance of the course
    sem = sort_by_term_code(list(uuid_df['Term Code']))[0]

    # Drop any from uuid that arent from the most recent semester
    uuid_df = uuid_df[(uuid_df['Term Code']==sem)]

    # Get various parameters of the search
    subj = uuid_df['Subject Code'].unique()[0]
    cnum = uuid_df['Course Number'].unique()[0]
    cname = uuid_df['Course Title'].unique()[0]
    cmean = uuid_df['Avg Course Rating'].unique()[0]
    dept_mean = uuid_df['Avg Department Rating'].unique()[0]
    dept_sd = uuid_df['SD Department Rating'].unique()[0]
    crank = uuid_df['Course Rank in Department in Semester'].unique()[0]
    
    ## Get the instructor details
    # Build a dictionary based on the instructors that have taught the course  
    # Fill out the instructors list with entries from the uuid_df
    instructors = []
    for i in uuid_df.index:
        # Add a new list entry to instructors for each instructor in the df
        instructors.append(instructor(uuid_df.at()[i,'Instructor First Name'], uuid_df.at()[i,'Instructor Last Name'], 
            uuid_df.at()[i,'Avg Instructor Rating In Section'], SEMESTER_MAPPINGS[str(uuid_df.at()[i,'Term Code'])],
            uuid_df.at()[i, 'Instructor Enrollment']))
    # Reverse Instructors
    instructors = list(reversed(instructors))
    # Get the course ranking for the department from the uuid
    subj_filter = {'$and':[
            {'Subject Code':subj},
            {"Term Code":sem}]}

    # Find all courses with given subject in ag_df
    subj_df, coll_name = query_df_from_mongo(db, subj_filter, collections = [coll_name])

    # Sort out the repeat courses such that we only get a single entry for course rating
    # Get the number of unique courses in a given department
    num_courses = subj_df['Course Number'].nunique()
    
    # Build the json response
    response = {'result':{'course name':str(cname),
            'most recent sem': SEMESTER_MAPPINGS[str(sem)],
            'course number': int(cnum),
            'course ranking': int(crank), 
                          'dept':{'dept name': str(subj), 'courses in dept': int(num_courses) , 'dept mean': float(dept_mean), 'dept sd':float(dept_sd)}, 
                          'current course mean': float(cmean), 
                          'instructors':instructors}}
    return response

def CourseFig3Timeseries(db, valid_uuid):

    """
    This function will search for all courses that have occurred in the given timespan. It will then
    return the average course rating over time and the average department rating over this time scale (from pre-computed values),
    along with a list of instructors who have taught on this timescale and their ratings over their semesters taught
    
    """
    response = {'result':{'course over time':{}, 'dept over time':{}, 'instructors':[]}}

    # filter that we use on the collection
    coll_filter = {'$and':[
            {"course_uuid":valid_uuid},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter)
    drop_duplicate_courses(df)

    # Fill the course number and name in the response
    response['result']['course number']=int(df['Course Number'].unique()[0])
    response['result']['course over time'] = {'ratings':[],'course name':df['Course Title'].unique()[0]}

    # Fill in the semesters that the course was found, in order of term
    term_codes = list(df['Term Code'].unique())

    term_codes = sort_by_term_code(term_codes)
    term_codes.reverse() # Reverse so that when they're appended in order

    terms = [SEMESTER_MAPPINGS[str(term)] for term in term_codes]
    response['result']['course over time']['semesters'] = terms
    response['result']['dept over time'] = {'dept name': df['Subject Code'].unique()[0],'ratings':[],'semesters': terms}

    # Add in the course rating and dept ratings
    for tcode in term_codes:
        response['result']['course over time']['ratings'].append(list(df[(df['Term Code']==tcode)]['Avg Course Rating'])[0])
        response['result']['dept over time']['ratings'].append(list(df[(df['Term Code']==tcode)]['Avg Department Rating'])[0])

    # # Add in the instructors
    for i in df['Instructor ID'].unique():
        sub_df = df[(df['Instructor ID']==i)]
        instr_obj = {}
        instr_obj['name'] = sub_df['Instructor First Name'].unique()[0] + ' ' + sub_df['Instructor Last Name'].unique()[0]
        instr_obj['semesters']=[]
        instr_obj['ratings'] = []
        for j in sub_df['Term Code'].unique():
            instr_obj['semesters'].append(SEMESTER_MAPPINGS[str(j)])
            instr_obj['ratings'].append(list(sub_df[(sub_df['Term Code']==j)]['Avg Instructor Rating In Section'])[0])
        response['result']['instructors'].append(instr_obj)
    return response # Added this bit to get rid of int64s, which are not JSON serializable

def CourseFig4TableBar(db, valid_uuid):

    """
    This function will perform the following steps:
    1. take a db connection and a uuid and then find the uuid in the aggregated db collection
    2. Get lists of the course number, subject code, instructors, and term codes for the course appearances in the time period of interest
    3. Search in the non-aggregated db for the same course number, subject code, and instructors
    4. Aggregate the entries by professor and question number, if the professor doesnt have an entry giving them a '0' rating
    5. Convert the dataframe into a json and serve
    
    """
        # Construct the json containing necessary data for figure 1 on course page
    response = {"result": {"instructors": [], 'questions':[]}}

    # filter that we use on the collection
    coll_filter = {'$and':[
            {"course_uuid":valid_uuid},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter)
    drop_duplicate_courses(df)

    # Now we need to drop the duplicates and only take columns of interest
    df = df.drop_duplicates(['Term Code', 'Instructor ID'])[['Term Code','Instructor ID','Subject Code', 'Course Number', 'Course Title']]
    df = df.rename(columns = {'Instructor ID':'Instructor ID', 'Course Title':'Section Title'})

    # Build a cursor to search the full db collection for these conditions
    # Build it based on each row in the df
    full_db_filter = {'$or':[]}
    for i in range(len(df)):
        # Create the row filter
        row_filter = {'$and':[]}
        for col in list(df.columns):
            if col in ['Instructor ID','Term Code','Course Number']:
                row_filter['$and'].append({col : int(df.iloc[i][col])}) # Encode the query as utf-8
            else:
                row_filter['$and'].append({col : str(df.iloc[i][col])}) # Encode the query as utf-8

        # Add row filter to full db filter
        full_db_filter['$or'].append(row_filter)

    # Use the filter to query the non-aggregated db
    full_db_coll_name = coll_name[11:] # This takes 'aggregated_GCOE' => GCOE

    # Use the database query to pull needed data
    df, coll_name = query_df_from_mongo(db, full_db_filter, collections=COLLECTION_NAMES)

    # Get the list of unique instructors
    instr_ids= list(df['Instructor ID'].unique())
    instrs = []
    for i in instr_ids:
        instrs.append(df[(df['Instructor ID']==i)].iloc[0]['Instructor First Name'] + ' ' + df[(df['Instructor ID'] == i)].iloc[0]['Instructor Last Name'])
    response['result']['instructors'] = instrs

    # Get the list of unique question
    questions = list(df['Question'].unique())
    tot_responses = 0
    tot_weighted_mean_responses = 0
    for q in questions:
        q_ratings = []
        sub_df = df[(df['Question']==q)]
        for iD in instr_ids:
            sub_sub_df = sub_df[(sub_df['Instructor ID']==iD)]
            if len(sub_sub_df)==0:
                q_ratings.append(0)
            else:
                weighted_means = sub_sub_df['Mean']*sub_sub_df['Responses']
                wms = weighted_means.sum()
                rs = sub_sub_df['Responses'].sum()
                tot_weighted_mean_responses+=wms
                tot_responses+=rs
                q_ratings.append(round(wms/rs, 4))
                # Ya Yeet
            del sub_sub_df
        response['result']['questions'].append({'question':q, 'ratings':q_ratings})
    response['result']['avg_rating'] = tot_weighted_mean_responses/tot_responses

    return response

###### APIs for Searchby instructor ########

def InstructorChipAPI(db, instructor_id):
    """
    This function takes a db connection and instructor_id and returns a dict containing the number of years that the 
    instructor has taught at OU, the most recent semester taught, and a list of departments that the instructor has taught within.
    """
    coll_filter = {"Instructor ID":instructor_id}
    df, _ = query_df_from_mongo(db,coll_filter)

    # Get the oldest term code and convert it to a term
    term_codes = list(df['Term Code'].unique())
    oldest_term = SEMESTER_MAPPINGS[str(sort_by_term_code(term_codes)[-1])]

    # Get the number of years teaching as a function of oldest term
    this_year = datetime.today().year
    diff = this_year - int(oldest_term[-4:])

    # Get a list of unique departments taught 
    subject_list = list(df['Subject Code'].unique())

    instructor_first_name = list(df['Instructor First Name'])[0]
    instructor_last_name = list(df['Instructor Last Name'])[0]
    instr_name = instructor_first_name+ ' '+instructor_last_name
    # Convert the results to a dict
    result = {'result':{'name': instr_name, 'most_recent_semester': oldest_term, 'num_years':diff, 'depts_taught':subject_list}}
    return result

#Feel free to rename this, just keeping it explicit so its easy to find
def InstructorFig1Table(db, instructor_id):
    """
    This will take in the name of an instructor, and return a dictionary containing all
    of the courses taught by this instructor.
    The courses will be returned with the dept name, course number, course name, specific course rating, and term
    """
    # Construct the json containing necessary data for figure 1 on course page
    ret_json = {"result": {"courses": []}}

    # filter that we use on the collection
    coll_filter = {'$and':[
            {"Instructor ID":instructor_id},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter)
    course_list = list(df.drop_duplicates('course_uuid', inplace=False)['course_uuid'])

    # Get a list of unique courses that are in the order of the semesters
    # Sort the term code list using prebuilt function
    term_code_list = sort_by_term_code(list(df.drop_duplicates(['course_uuid','Term Code'], inplace=False)['Term Code']))

    # Create the dict for this sorted term code list
    dict_term_list = {k: v for v, k in enumerate(term_code_list)}

    # Add the column as a mapping to the df
    df['sorter'] = df['Term Code']
    df['sorter'].replace(dict_term_list, inplace=True)
    df.sort_values('sorter', inplace=True)
    course_list = list(df.drop_duplicates('course_uuid', inplace=False)['course_uuid'])

    # Get the large df with all of the instructors
    coll_filter = {'$and':[
    {"course_uuid":{'$in':course_list}},
    {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df_main, coll_name = query_df_from_mongo(db, coll_filter, collections = [coll_name])

    for crs in course_list:
        df_crs = df_main[(df_main['course_uuid']==crs)] # Made df_crs once and then slice it for each instructor

        avg = df_crs['Avg Instructor Rating In Section'].mean()

        # Define a list of the term codes this instructor has taught
        term_code_list = df_crs[df_crs['Instructor ID']==instructor_id]['Term Code']
        term_code_list = sort_by_term_code(term_code_list)
        term_code_list = [SEMESTER_MAPPINGS[str(i)] for i in term_code_list]
        terms_taught = ''
        for j in term_code_list:
            terms_taught += j
            if j != term_code_list[-1]:
                terms_taught+=', '
            else:
                break
        inst = {
            "course name": df_crs['Course Title'].unique()[0],
            'course number': int(df_crs['Course Number'].unique()[0]),
            'dept name': df_crs['Subject Code'].unique()[0],
            "instr_rating_in_course": df_crs[df_crs['Instructor ID'] == instructor_id]["Avg Instructor Rating In Section"].mean(),
            'avg_course_rating': avg,
            "term": terms_taught
            }

        ret_json["result"]["courses"].append(inst)

    ret_json['result']['instructor name'] = str(df['Instructor First Name'].unique()[0])+ ' ' + str(df['Instructor Last Name'].unique()[0])
                
    return ret_json

def InstructorFig2Timeseries(db, instructor_id):
    """
    This will take in the name of an instructor, and return a dictionary containing the following:
    Instructor Name - First and Last name
    Instructor over time - Semesters taught, and their respective avg ratings
    Dept over time - dept name, same semesters as above, dept avg rating for these semesters
    Courses - name of course, semesters taught, and respective avg ratings
    """
    # Construct the json containing necessary data for figure 2 on instructor page
    ret_json = {'result':
                    {'instructor name': '',
                        'instructor over time':{
                            'semesters':[],
                            'ratings':[]},
                        'dept over time':{
                            'dept name': "",
                            'semesters':[],
                            'ratings':[]},
                        'courses':[]
                    }
                }

    # filter that we use on the collection
    coll_filter = {'$and':[
            {"Instructor ID":instructor_id},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter)

    # get a dict containing all current semesters that have been taught by this dude as keys, values are gonna be total rating
    semesters_taught = {}

    # this is gonna have current semesters taught as keys, and value is gonna be the amount of courses taught in that semester
    # I know this is mem-inefficient, will optimize later after demo
    semester_totals = {}

    # used to keep track of which courses have already been added to the return json
    courses = []

    # used to keep track of which departments this professor has taught in
    departments = []

    # Sort the df by term code
    sorted_list_terms = sort_by_term_code(set(list(df['Term Code'])))

    # Create the dict for this sorted term code list
    dict_term_list = {k: v for v, k in enumerate(sorted_list_terms)}

    # Add the column as a mapping to the df
    df['sorter'] = df['Term Code']
    instructor_list_ind = df['sorter'].replace(dict_term_list, inplace=True)
    df.sort_values(by=['sorter'], ascending=False,inplace=True)

    for index, row in df.iterrows():
        # set instructor name on first iteration
        if index == 0:
            ret_json["result"]["instructor name"] = row["Instructor First Name"] + " " + row["Instructor Last Name"]

        # instructor over time block
        if SEMESTER_MAPPINGS[str(row["Term Code"])] not in semesters_taught:
            semesters_taught[SEMESTER_MAPPINGS[str(row["Term Code"])]] = row["Avg Instructor Rating In Section"]
            semester_totals[SEMESTER_MAPPINGS[str(row["Term Code"])]] = 1
        else:
            semesters_taught[SEMESTER_MAPPINGS[str(row["Term Code"])]] += row["Avg Instructor Rating In Section"]
            semester_totals[SEMESTER_MAPPINGS[str(row["Term Code"])]] += 1

        # courses block
        if row["Course Title"] not in courses:
            courses.append(row["Course Title"])
            ret_json["result"]["courses"].append({"name": row["Course Title"], 
                                                    "semesters": [SEMESTER_MAPPINGS[str(row["Term Code"])]],
                                                    "ratings": [row["Avg Instructor Rating In Section"]]})
        else:
            for i in range(0, len(ret_json["result"]["courses"])):
                if ret_json["result"]["courses"][i]["name"] == row["Course Title"]:
                    ret_json["result"]["courses"][i]["semesters"].append(SEMESTER_MAPPINGS[str(row["Term Code"])])
                    ret_json["result"]["courses"][i]["ratings"].append(row["Avg Instructor Rating In Section"])

        if row["Subject Code"] not in departments:
            departments.append(row["Subject Code"])


    # Now we use this complex averaging algorithm to get semesterly average ratings, add to ret_json
    for key, value in semesters_taught.items():
        semesters_taught[key] = value / semester_totals[key]
        ret_json["result"]["instructor over time"]["semesters"].append(key)
        ret_json["result"]["instructor over time"]["ratings"].append(semesters_taught[key])

    # Now we need a new data frame for the entire department
    coll_filter = {'$and':[
            {"Subject Code": departments[0]},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter)

    # construct dictionaries where keys are current semesters in which professor taught, and value is total rating for all courses/course count
    dept = {}
    count = {}
    for key in semesters_taught.keys():
        dept[key] = 0
        count[key] = 0

    for index, row in sorted(df.iterrows(), reverse=True):
        # set dept name on first iteration
        if index == 0:
            ret_json["result"]["dept over time"]["dept name"] = row["Subject Code"]

        # ratings block
        if SEMESTER_MAPPINGS[str(row["Term Code"])] in dept.keys():
            dept[SEMESTER_MAPPINGS[str(row["Term Code"])]] += row["Avg Instructor Rating In Section"]
            count[SEMESTER_MAPPINGS[str(row["Term Code"])]] += 1

    # average dept semesterly ratings and add to ret_json
    for key, value in dept.items():
        if count[key]!=0:
            dept[key] = value / count[key]
        else:
            dept[key] = 0
        ret_json["result"]["dept over time"]["semesters"].append(key)
        ret_json["result"]["dept over time"]["ratings"].append(dept[key])

    return ret_json

def InstructorFig3TableBar(db, instructor_id):
    # Construct the json dictionary containing the necessary information for figure 3
    ret_json = {'result':{
                            'instructor name': '',
                            'courses':[],
                            'questions':[]
                        }
                }

    # filter that we use on the collection
    coll_filter = {'$and':[
            {"Instructor ID":instructor_id},
            {"Term Code": {'$in': CURRENT_SEMESTERS}}]}

    df, coll_name = query_df_from_mongo(db, coll_filter, collections=COLLECTION_NAMES)

    # total rating and count to be used for avg_rating
    total_rating = 0
    count = 0

    # Create a list of Courses
    df['course long name'] = df['Subject Code']+df['Course Number'].astype(str)+': '+df['Section Title']
    df['course'] = df['Subject Code']+df['Course Number'].astype(str)

    # Get list of unique courses and add to ret_json
    unique_courses = list(df['course'].unique())
    ret_json['result']['courses']=unique_courses

    # Get list of unique questions and add to ret_json
    unique_questions = df['Question'].unique()
    for i in unique_questions:
        ret_json['result']['questions'].append({'question':i, 'ratings':[]})

    # Look through each course for each question. If found, add avg rating to list. If not found, add 'none'
    for crs in unique_courses:
        subset = df[(df['course']==crs)]
        # This if will catch and remove courses without individual question ratings
        if subset[['Question', 'Mean', 'Responses']].isnull().values.any():
            ret_json['result']['courses'].remove(crs)
            continue
        for j in range(len(ret_json['result']['questions'])):
            question = ret_json['result']['questions'][j]['question']
            if question in list(subset['Question']):
                ss = subset[(subset['Question']==question)]
                if np.sum(ss['Responses'])!= 0:
                    rating = np.sum(ss['Mean']*ss['Responses'])/np.sum(ss['Responses'])
                elif len(ss['Mean']) != 0:
                    rating = np.sum(ss['Mean'])/len(ss['Mean'])
                else:
                    rating = 0
            else:
                rating = 0
            ret_json['result']['questions'][j]['ratings'].append(round(rating,4))

    ret_json['result']['instructor name'] = df['Instructor First Name'][0]+' '+ df['Instructor Last Name'][0]

    return ret_json

######################

# Define the function to pull all of the courses or instructors as a dict of labels and values
def SearchAutocomplete(db, search_type='course'):
    """
    This function will return a dict object of courses or instructors, depending upon the search type. Each object in dict will
    have a label (Professor name, first then last, if instructor, otherwise long course string) and a value (instructor id if 
    search_type is instructor, course_uuid if search_type is course). 

    Input:
    db - a connection to the mongoDB
    search_type - a string, either 'course' or 'instructor'

    """
    # Create a map to map search type inputs to keys in the dataframe
    search_type_to_key = {'course':'course_uuid', 'instructor':'Instructor ID'}

    # Make sure the search_type is valid
    try:
        search_key = search_type_to_key[search_type]
    except:
        raise Exception('Invalid Search Type for SearchForm API. Search Type: '+search_type+' provided, and should be course or instructor.')

    # filter that we use on the collection
    coll_filter = {"Term Code": {'$in': CURRENT_SEMESTERS}}
    
    df = pd.DataFrame()
    for coll_name in AGG_COLLECTION_NAMES:
        coll = db.get_db_collection(DB_NAME, coll_name)
        # Use the database query to pull needed data
        cursor = coll.find(coll_filter)
        # For whatever reason, generating a dataframe clears the cursor, so get population here
        population = coll.count_documents(coll_filter)
        # This assumes that there will be no same uuid's across the different collections, e.g. the same uuid in GCOE and JRCOE
        if population > 0:
            df_coll = pd.DataFrame(list(cursor))
            df_coll.drop_duplicates(search_key, inplace=True)
            df = pd.concat([df, df_coll], ignore_index=True, sort=True)
    df.drop_duplicates(search_key, inplace=True)

    # Now, we just need to convert the dataframe to a dictionary with needed form for search autocomplete
    if search_type == 'course':
        # Create the label column
        df['label'] = df['Subject Code'].str.strip()+df['Course Number'].astype(str)+': '+df['Course Title']
        return_list = [{'label':row['label'], 'value':row[search_key]} for index, row in df.iterrows()]
    else:
        df['label'] = df['Instructor First Name']+' '+ df['Instructor Last Name']
        return_list = [{'label':row['label'], 'value':row[search_key]} for index, row in df.iterrows()]
    return return_list

if __name__ == '__main__':
    # Test the db search
    # test = [201410, 201420, 201530, 201620, 201230, 201810]
    # print(test)
    # sort_by_term_code([201710, 201820, 201620, 201410, 201110, 201630, 201610])

    # uuid_df, coll_name = query_df_from_mongo(mongo_driver(),cursor)
    pprint.pprint(CourseFig1Table(mongo_driver(), "753572960")) # Statics
    pprint.pprint(CourseFig2Chart(mongo_driver(), "753572960"))
    pprint.pprint(CourseFig3Timeseries(mongo_driver(), "753572960"))
    pprint.pprint(CourseFig4TableBar(mongo_driver(), "753572960")) # Make sure the full unmodified dataset is uploaded before running
    pprint.pprint(InstructorFig1Table(mongo_driver(), 624629390)) # Janet Allen
    pprint.pprint(InstructorFig2Timeseries(mongo_driver(), 624629390))
    pprint.pprint(InstructorFig3TableBar(mongo_driver(), 624629390)) # Make sure the full unmodified dataset is uploaded before running
    pprint.pprint(InstructorChipAPI(mongo_driver(), 624629390))
