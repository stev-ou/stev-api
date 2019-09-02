'''
This script will contain functions used to aggregate the input data into more usable metrics. It will create an aggregated dataframe with the refined data and 
 will return this aggregated dataframe to be used alongside the unmodified input data. 
 '''

 # global/pypi
import numpy as np
import pandas as pd
from copy import deepcopy

def combine_standard_deviations(sd_list, mean_list,pop_list):
    '''
    This function will take lists of standard deviations, means, and population sizes for each list unit. The function
    will combine the lists to produce a standard deviation for the group, based on the input parameters. Formula for combining the SD taken from the below link:
    
    https://www.researchgate.net/post/How_to_combine_standard_deviations_for_three_groups
    
    * All lists must be same length
    '''
    # Check for equal sized lists
    if not len(sd_list) == len(mean_list)==len(pop_list):
        print('All input lists to the function -- combine_standard_deviations -- must be of the same length.')
    # Compute the weighted mean by populations
    pop_mean = np.sum(mean_list*pop_list)/(np.sum(pop_list))
    # Compute the deviance
    deviance = np.sum((pop_list)*(sd_list**2) + (pop_list)*(mean_list - pop_mean)**2)
    # Compute the standard deviation
    sd = np.sqrt(deviance/(np.sum(pop_list)))
    return sd

def aggregate_data(df):
    """
    Aggregates a pandas dataframe of student reviews data. See the First, Second, and Third Operations below for more descriptions of functions.
    Note the similar form across operations.
    :Inputs:
    - df: A pandas dataframe, slightly modified from db results (see conditioning in data_loader.py)
    :Returns:
    - ag_df: An aggregated version of the same dataframe
    """
    # Can't handle if Responses are 0; Convert 0 responses to 1
    df['Responses'] = df['Responses'].apply(lambda x: x if x>0 else 1)
    ag_df = deepcopy(df)
    
    # Remove the repeat rows that will occur because we are taking 1-10 question responses down to 1
    ag_df = ag_df.drop_duplicates(subset = ['Term Code', 'course_uuid', 'Instructor ID'])
    
    # First Operation: Combine sections of the same course taught by the same instructor in the same semester
    # we'll use these local functions
    weighted_mean_instr = lambda x: np.average(x.values, weights=df.loc[x.index, 'Responses'].values)
    weighted_stdevs_instr = lambda x: combine_standard_deviations(x.values, \
                                                                    mean_list = df.loc[x.index, 'Mean'].values, \
                                                                    pop_list = df.loc[x.index, 'Responses'].values)
    ag_df['Avg Instructor Rating In Section'] = df.groupby(['Term Code', 'course_uuid', 'Instructor ID'])['Mean'].transform(weighted_mean_instr)
    ag_df['SD Instructor Rating In Section'] = df.groupby(['Term Code', 'course_uuid', 'Instructor ID'])['Standard Deviation'].transform(weighted_stdevs_instr)
    ag_df['Instructor Enrollment'] = ag_df.groupby(['Term Code', 'course_uuid', 'Instructor ID'])['Responses'].transform('sum') # Instr enrollment is sum of section enrollment
    
    
    # Second Operation: Combine Instructors in Courses to get the Average Course metrics
    # we'll use these local functions, which tell the groupby which columns to analyze
    weighted_mean_course = lambda x: np.average(x.values, weights=ag_df.loc[x.index, 'Instructor Enrollment'].values)
    weighted_stdevs_course = lambda x: combine_standard_deviations(x.values, \
                                                                    mean_list = ag_df.loc[x.index, 'Avg Instructor Rating In Section'].values, \
                                                                    pop_list = ag_df.loc[x.index, 'Instructor Enrollment'].values)
    ag_df['Avg Course Rating'] = ag_df.groupby(['Term Code', 'course_uuid'])['Avg Instructor Rating In Section'].transform(weighted_mean_course)
    ag_df['SD Course Rating'] = ag_df.groupby(['Term Code', 'course_uuid'])['SD Instructor Rating In Section'].transform(weighted_stdevs_course)
    ag_df['Course Enrollment'] = ag_df.groupby(['Term Code', 'course_uuid'])['Instructor Enrollment'].transform('sum') # Course enrollment sum of constituent instr enrollments
    ag_df['Course Rank in Department in Semester']= ag_df.groupby(['Term Code', 'College Code', 'Subject Code'])['Avg Course Rating'].rank(method ='dense',na_option='top', ascending=False).apply(int)

    
    # Third Operation: Combine Courses inside of a department to get average department metrics
    weighted_mean_dept = lambda x: np.average(x.values, weights=ag_df.loc[x.index, 'Course Enrollment'].values)
    weighted_stdevs_dept = lambda x: combine_standard_deviations(x.values, \
                                                                    mean_list = ag_df.loc[x.index, 'Avg Instructor Rating In Section'].values, \
                                                                    pop_list = ag_df.loc[x.index, 'Course Enrollment'].values)
    ag_df['Avg Department Rating'] = ag_df.groupby(['Term Code', 'College Code', 'Subject Code'])['Avg Course Rating'].transform(weighted_mean_dept)
    ag_df['SD Department Rating'] = ag_df.groupby(['Term Code', 'College Code', 'Subject Code'])['SD Course Rating'].transform(weighted_stdevs_dept)
    
    # Rename the necessary columns
    ag_df = ag_df.rename(columns = {'Section Title':'Course Title'})
    # Drop unnecessary columns, mainly leftovers from df
    ag_df = ag_df.drop(columns = ['Question', 'Question Number', 'Responses','Mean', 'Standard Deviation'], errors = 'ignore')
    return ag_df