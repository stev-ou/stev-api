import unittest
import mongo
import json
import data_aggregation
import pandas as pd
import random
from pprint import pprint
from api_functions import *
from constants import DB_NAME, COLLECTION_NAME, AGGREGATED_COLLECTION_NAME

class basictest(unittest.TestCase):
    """ Basic tests """
    # Test for mongo.py
    def test_connection(self):
        '''
        This unittest will test whether the mongo driver is connecting successfully to:
        Database name: DB_NAME
        collection name: COLLECTION_NAME
        '''
        try:
            conn = mongo.MongoDriver()
            conn.get_db_collection(DB_NAME, COLLECTION_NAME)
            conn_status = True
        except:
            conn_status = False

        return self.assertEqual(True, conn_status)

    # Tests for database aggregation
    # Test the computation of the mean and sd for the data aggregation
    def test_compute_sd(self):
        '''
        This unit test will examine the formulae for computing weighted mean and sd from the data aggregation script.
        '''

        # Test the combined means
        sd = data_aggregation.combine_standard_deviations(np.array([4,6]),np.array([50,9]), np.array([47,100])) # sd, means, populations, weights
        # Note that the above returns a tuple of combined (mean, sd) and thus tests for both mean and sd

        if round(sd, 2) == 19.88:
            status = True
        else: 
            status = False

        # Validated the above functions for combined sd and combined means with this website, albeit 
        # there was No entry or validation for the weighting
        # https://www.statstodo.com/CombineMeansSDs_Pgm.php
        # * Note that my formula uses n instead of n-1 for combining SDs, so expect some small differences in the final result
        return self.assertEqual(True, status)

    # Test the current course apis to make sure that they are at least returning a valid json
    def test_course_api_endings(self):
        '''
        This unit test will ping each of the currently created api endings with a variety of different courses to make sure they hit.

        '''
        # Define the currently working courses - You can generate this by running api_functions.py
        course_function_list = [CourseFig1Table, CourseFig2Chart, CourseFig3Timeseries, CourseFig4TableBar] 
        # Generate random course/instructor IDs for the test
        response = SearchAutocomplete(mongo.MongoDriver(), 'course')
        res_dict = json.loads(json.dumps(response))
        id_list = [el['value'] for el in res_dict]
        test_id_list = random.choices(id_list, k=8)
        print('Testing for the following instructor IDs, generated randomly from viable options: ')
        pprint.pprint(test_id_list)

        # Create connection to the db
        db = mongo.MongoDriver()

        # Try the function for autocomplete for all courses
        try:
            print('SearchAutocomplete for all courses')
            response = SearchAutocomplete(db, search_type='course')
            response_dict = json.loads(json.dumps(response))

        except:
            return self.assertEqual(True, False)

        for course in test_id_list:
            print(course)
            for func in course_function_list:
                try:
                    response = func(db, course)
                    json.loads(json.dumps(response))
                except:
                    return self.assertEqual(True, False)

        return self.assertEqual(True, True)

    # Test the current instructor apis to make sure that they are at least returning a valid json
    def test_instructor_api_endings(self):
        '''
        This unit test will ping each of the currently created api endings with a variety of different instructors to make sure they hit.

        '''
        # Define the currently working course APIs
        instructor_function_list = [InstructorFig1Table, InstructorFig2Timeseries, InstructorFig3TableBar]

        # Generate random course/instructor IDs for the test
        response = SearchAutocomplete(mongo.MongoDriver(), 'instructor')
        res_dict = json.loads(json.dumps(response))
        id_list = [el['value'] for el in res_dict]
        test_id_list = random.choices(id_list, k=8)
        print('Testing for the following instructor IDs, generated randomly from viable options: ')
        pprint.pprint(test_id_list)

        # Create connection to the db
        db = mongo.MongoDriver()
        try:
            print('SearchAutocomplete for all instructors')
            response = SearchAutocomplete(db, search_type='instructor')
            response_dict = json.loads(json.dumps(response))
        except:
            return self.assertEqual(True, False)

        print('Testing the api functions for the following instructors: ')
        for instr in test_id_list:
            print(instr)
            for func in instructor_function_list:
                try:
                    response = func(db, instr)
                    json.loads(json.dumps(response))
                except:
                    return self.assertEqual(True, False)

        return self.assertEqual(True, True)

    # # Test the dataframe aggregation for unique entries 
    def test_zdataframe_aggregation(self): # Z puts it last

        '''
        This unit test will examine the aggregated dataframe and ensure it has no course entry repeats with the same 
        course title and instructor.
        '''
        # Test the data aggregation for unique entries
        df = pd.read_csv('data/GCOE.csv')
        df.rename({'Instructor 1 ID':'Instructor ID', 'Instructor 1 First Name':'Instructor First Name', 'Instructor 1 Last Name':'Instructor Last Name'}, axis=1, inplace=True)
        # Condition the df prior to aggregation
        df = df.drop(['_id'],axis=1, errors = 'ignore').rename(columns ={'Individual Responses':'Responses'})
        df['Instructor ID'] = (df['Instructor First Name']+df['Instructor Last Name']).apply(str).apply(hash).astype('int32').abs()
        df['course_uuid'] = (df['Subject Code']+df['Course Number'].apply(str)+df['Section Title'].apply(lambda x: x[:-4])).apply(str).apply(hash).astype('int32').abs().apply(str) 
        df['Question Number'] = df['Question Number'].astype(int)
        df['Term Code'] = df['Term Code'].astype(int)
        # Make sure the First and Last names are in camelcase; i.e. no CHUNG-HAO LEE
        df['Instructor First Name'] = df['Instructor First Name'].apply(str.title)
        df['Instructor Last Name'] = df['Instructor Last Name'].apply(str.title)

        ag_df = data_aggregation.aggregate_data(df)

        # There should be no entries with the same course name, Instructor ID, and Term Code, so the below should be false
        num_repeats = len(ag_df[ag_df[['Subject Code', 'Course Number', 'Course Title', 'Term Code','Instructor ID']].duplicated() == True])

        return self.assertEqual(0, num_repeats)

if __name__ == '__main__':
    # test_current_api_endings()
    unittest.main()
