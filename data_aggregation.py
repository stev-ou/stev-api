'''
This script will contain functions used to aggregate the input data into more usable metrics. It will create an aggregated dataframe with the refined data and 
 will upload this aggregated dataframe to MongoDB to be used alongside the unmodified input data. Further documentation on the combination of means and standard deviations is available 
 in the data_aggregation_exploration.ipynb.

 '''

import numpy as np
import pandas as pd
import yaml
import os
import math
from tqdm import tqdm

# Get file location for mappings.yaml and reading data
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def combine_means(mean_list, pop_list, weight_list):
    '''
    This function takes lists of means, population sizes, and weights for each population, and combines the result into a single mean value.
    * All lists must be the same length
    '''
    mean_list = np.array(mean_list)
    pop_list = np.array(pop_list)
    weight_list = np.array(weight_list)
    # Check for equal sized lists
    if not len(mean_list)==len(pop_list)==len(weight_list):
        print('All input lists to the function -- combine_standard_deviations -- must be of the same length.')
        # Proceed with the program
    # Combine the population-and-weight-modulated means
    mean = np.sum(mean_list*pop_list*weight_list)/(np.sum(pop_list*weight_list))
    return mean
    

def combine_standard_deviations(sd_list, mean_list,pop_list, weight_list):
    '''
    This function will take lists of standard deviations, means, population sizes, and weights for each list unit. The function
    will combine the lists to produce a standard deviation for the group, based on the input parameters. Formula for combining the SD taken from the below link:
    
    https://www.researchgate.net/post/How_to_combine_standard_deviations_for_three_groups
    
    * All lists must be same length
    '''
    # Convert all input lists into numpy arrays
    sd_list = np.array(sd_list)
    mean_list = np.array(mean_list)
    pop_list = np.array(pop_list)
    weight_list = np.array(weight_list)
    # Check for equal sized lists
    if not len(sd_list) == len(mean_list)==len(pop_list)==len(weight_list):
        print('All input lists to the function -- combine_standard_deviations -- must be of the same length.')
    # Proceed with the program
    # Compute the weighted mean of the populations
    pop_mean = combine_means(mean_list, pop_list, weight_list)
    # Compute the deviance
    deviance = np.sum((pop_list)*(weight_list)*(sd_list**2) + (pop_list*weight_list)*(mean_list - pop_mean)**2)
    # Compute the standard deviation
    sd = np.sqrt(deviance/(np.sum(pop_list*weight_list)))
    return pop_mean,sd


def aggregate_data(df):

    # Drop rows where the NaN value exists from the dataframe
    df.dropna(inplace=True)

    # Initialize the aggregated dataframe by copying the base data frame
    ag_df = df.copy()

    # Drop the unnecessary columns
    ag_df.drop(['Department Code', 'Department Standard Deviation','Question Number','Section Number','CRN','Campus Code','Question', 'Mean', 'Median', 'Standard Deviation', 'Department Mean', 'Department Median', 'Similar College Mean', 'College Mean', 'College Median', 'Percent Rank - Department', 'Percent Rank - College', 'Percent #1', 'Percent #2', 'Percent #3', 'Percent #4', 'Percent #5', 'ZScore - College', 'ZScore - College Similar Sections', 'Course Level', 'Section Size', 'Similar College Median'], axis=1, inplace = True, errors='ignore')

    # Add in the columns to be filled with the aggregated values
    ag_df.insert(3,'Avg Department Rating', 0.0)
    ag_df.insert(4,'SD Department Rating', 0.0)
    ag_df.insert(7,'Avg Course Rating', 0.0)
    ag_df.insert(8,'SD Course Rating', 0.0)
    ag_df.insert(9,'Course Rank in Department in Semester', 0)
    ag_df.insert(12, 'Avg Instructor Rating In Section', 0.0)
    ag_df.insert(13, 'SD Instructor Rating In Section', 0.0)
    ag_df.insert(15, 'Course Enrollment', 0)

    # Rename the Instructor 1 First Name, Last Name columns and other necessary columns
    ag_df.rename(columns = {'Section Title':'Course Title', 'Responses':'Instructor Enrollment', 'Instructor 1 First Name':'Instructor First Name', 'Instructor 1 Last Name':'Instructor Last Name'}, inplace= True)
    # Remove the repeat rows that will occur because we are taking 1-10 question responses down to 1
    ag_df.drop_duplicates(subset = ag_df.columns.drop(['Course Title', 'Instructor Enrollment'], errors='ignore'), inplace = True)
    # Read in the question mappings values from the mappings.yaml
    file_path = __location__+"/mappings.yaml"

    with open(file_path) as f:
        # use safe_load instead load
        mappings = yaml.safe_load(f)
        question_weighting = mappings['Instructor_question_weighting']

    # Lets fill the average instructor rating in each section, i.e. the combined rating for each question per section per term
    dropped_entries = 0
    ag_dropped_entries = 0
    for term in tqdm(df['Term Code'].unique()):
        subset = df[(df['Term Code']==term)] # Subset the df based on the current term
        for subject in subset['Subject Code'].unique(): # Iterate over all subjects (test case - for subject in ['DSA']:)
            subset = df[(df['Term Code']==term) & (df['Subject Code']==subject)] # Subset the df based on the current subject
            for course in subset['Course Number'].unique(): # Iterate over courses with the desired subject 
                subset = df[(df['Term Code']==term) & (df['Subject Code']==subject) & (df['Course Number']==course)]# Subset the df based on the current course
                for instructor in subset['Instructor ID'].unique(): # Iterate over instructors with desired subject and course number
                    subset = df[(df['Term Code']==term) & (df['Subject Code']==subject) & (df['Course Number']==course) & (df['Instructor ID']==instructor)] # Modify the subset based on the current instructor 
                    if len(subset)!=0: 
                        # Set the combined mean and combined sd value into the aggregated dataframe
                        # Find the row of interest in the aggregated df
                        ag_df_section_row = ag_df[((ag_df['Term Code']==term) & (ag_df['Subject Code']==subject) & (ag_df['Course Number']==course) & (ag_df['Instructor ID']==instructor))].index.tolist() 
                        
                        if len(ag_df_section_row)!=1:
                            print('Aggregated Dataframe contains incorrect number of entries (number entries = ' + str(len(ag_df_section_row))+ ') for term' + str(term)+ ', subject: '+ str(subject)+ ', course: '+ str(course)+ ', and instructor: '+ str(instructor))
                            print(ag_df[((ag_df['Term Code']==term) & (ag_df['Subject Code']==subject) & (ag_df['Course Number']==course) & (ag_df['Instructor ID']==instructor))])
                            # Drop the offending entries
                            ag_df.drop(ag_df_section_row, axis = 0, inplace=True)
                            df.drop(subset.index.tolist(), axis=0, inplace=True)
                            ag_dropped_entries +=len(ag_df_section_row)
                            dropped_entries += len(subset.index.tolist())
                            print('\n')
                        else:
                            # Compute the combined mean and standard deviation of the questions
                            # Input the standard deviation, mean, number of responses, and the question number mapped to the weights for each subject-course-instructor combination
                            instructor_mean, instructor_sd = combine_standard_deviations(subset['Standard Deviation'], subset['Mean'], subset['Responses'], subset['Question Number'].map(str).map(arg=question_weighting[str(subset['College Code'].unique()[0])]))
                            
                            if math.isnan(instructor_mean) or math.isnan(instructor_sd):
                                print('Nan for instructor mean')
                                print(subset['Mean'])
                                print(subset['Standard Deviation'])
                                print(subset['Responses'])
                                print(subset['Question Number'].map(str).map(arg=question_weighting[str(subset['College Code'].unique()[0])]))
                                print('Nan for (number entries = ' + str(len(ag_df_section_row))+ ') for term' + str(term)+ ', subject: '+ str(subject)+ ', course: '+ str(course)+ ', and instructor: '+ str(instructor))
                                return 1
                            # Fill the Instructor Ratings Columns
                            ag_df.at[ag_df_section_row[0], 'Avg Instructor Rating In Section'] = instructor_mean
                            ag_df.at[ag_df_section_row[0], 'SD Instructor Rating In Section'] = instructor_sd

                            # Fill the Num Responses column, based on the minimum number of responses in the group of questions
                            # if they teach two or more sections, add the number of students in each course to get the total number
                            subset = subset.drop_duplicates(subset=['Course Number', 'Section Number'])
                            total_responses = 0

                            for i in list(subset['Responses']):
                                total_responses = total_responses + i
                            # Set the Num Responses in the agg df equal to the total responses in this course
                            ag_df.at[ag_df_section_row[0], 'Instructor Enrollment'] = total_responses

                    else:
                        print('Could not find the combination for subject: '+ str(subject) + ', course: '+ str(course)+ ', and instructor: '+ str(instructor))
                # Back to Course level of tree, now that we've filled out the instructor level info
                # Compute the combined mean and standard deviation of all of the instructors within the course

                # Find the row of interest in the desired df
                ag_df_course_rows = ag_df[(ag_df['Term Code']==term) & (ag_df['Subject Code']==subject) & (ag_df['Course Number']==course)].index.tolist()
                
                # Modify the dataframe subset that consists only of the entries with the desired course (see course index above)
                # Note that now our subset consists of aggregated data from all instructors within the desired course
                subset = ag_df[(ag_df['Term Code']==term) & (ag_df['Subject Code']==subject) & (ag_df['Course Number']==course)]
                if len(subset) !=0:
                    #### IMPORTANT #### Population weighting used in calculation of mean and sd for course ratings, based on instructor ratings
                    course_mean, course_sd = combine_standard_deviations(subset['SD Instructor Rating In Section'], subset['Avg Instructor Rating In Section'], subset['Instructor Enrollment'], np.ones(len(subset['SD Instructor Rating In Section'])))

                    # Quick Nan check to make sure we arent computing Nan values
                    if math.isnan(course_mean) or math.isnan(course_sd):
                        print('Nan for course mean')
                        print('\n')
                        print(subset['SD Instructor Rating In Section'])
                        print(subset['Avg Instructor Rating In Section'])
                        print(subset['Instructor Enrollment'])
                        print('Nan within (number entries = ' + str(len(subset))+ ') for term' + str(term)+ ', subject: '+ str(subject)+ ', and course: '+ str(course)+'.')
                        print(subset)
                        return 1

                    # Fill the Course ratings columns
                    ag_df.at[ag_df_course_rows, 'Avg Course Rating'] = course_mean
                    ag_df.at[ag_df_course_rows, 'SD Course Rating'] = course_sd
                    ag_df.at[ag_df_course_rows, 'Course Enrollment'] = np.sum(np.array(subset['Instructor Enrollment']))
                else:
                    print('Error: forced to eliminate the course with subject/department: '+ str(subject)+ ', and number: '+ str(course)+' in term'+ str(term))
            # Back to Department level of tree, now that we've filled out the instructor and course level info
            # Modify the dataframe subset that consists only of the entries with the desired subject(see course index above)
            # Find the row of interest in the desired df
            ag_df_dept_rows = ag_df[(ag_df['Subject Code']==subject) & (ag_df['Term Code']==term)].index.tolist()

            # Note that now our subset consists of aggregated data from all instructors and courses within the desired subject/department
            subset = ag_df[(ag_df['Subject Code']==subject) & (ag_df['Term Code']==term)]
            if len(subset)!=0:
                # Compute the combined mean and standard deviation of all of the courses within the department
                #### IMPORTANT #### Population Weighting used in calculation of department parameters

                department_mean, department_sd = combine_standard_deviations(subset['SD Course Rating'], subset['Avg Course Rating'], subset['Course Enrollment'], np.ones(len(subset['Avg Course Rating'])))
                # Quick Nan check to make sure we arent computing Nan values
                if math.isnan(department_mean) or math.isnan(department_sd):
                    print('Nan for department mean')
                    print('\n')
                    print(subset['SD Course Rating'])
                    print(subset['Avg Course Rating'])
                    print(subset['Course Enrollment'])
                    print('Nan within (number entries = ' + str(len(subset))+ ') for term' + str(term)+ ', subject/department: '+ str(subject))
                    print(subset)
                    return 1
                # Fill the Department ratings columns
                ag_df.at[ag_df_dept_rows, 'Avg Department Rating'] = department_mean
                ag_df.at[ag_df_dept_rows, 'SD Department Rating'] = department_sd

                # Fill in the rankings within the department
                ag_df.loc[((ag_df['Subject Code']==subject) & (ag_df['Term Code']==term)),'Course Rank in Department in Semester'] = ag_df.loc[((ag_df['Subject Code']==subject) & (ag_df['Term Code']==term)), :]['Avg Course Rating'].rank( method ='dense',na_option='top', ascending=False)
            else:
                print('Error: forced to eliminate the department: '+ str(subject)+ ' for term code '+str(term))
    # # Add in a Queryable Course String for the search by course
    # ag_df['Queryable Course String'] = ag_df['Subject Code'].map(str).str.lower() + ' ' + ag_df['Course Number'].map(str).str.lower() + ' ' + ag_df['Course Title'].map(str).str.lower()

    # Add in a uuid field for the course, based on subject code (lowercase) and course number
    ag_df['course_uuid'] = ag_df['Subject Code'].map(str).str.lower() + ag_df['Course Number'].map(str)# .str.lower()

    # Convert rankings to int
    ag_df['Course Rank in Department in Semester'] = ag_df['Course Rank in Department in Semester'].astype(int)
    print(str(dropped_entries)+ ' entries were dropped from main dataset, corresponding to '+str(ag_dropped_entries)+' dropped from the aggregated dataframe.')
    print('\n')
    return ag_df

if __name__ == '__main__':
    
    df = pd.read_csv("data/GCOE.csv") # Modify to correct data location
    
    ag_df = aggregate_data(df)
    # Tests the dataframe department ranking
    print(ag_df.loc[((ag_df['Term Code']==201810) & (ag_df['Subject Code']=='AME')), ['Course Number','Avg Course Rating','Course Rank in Department in Semester']].sort_values('Avg Course Rating'))
    
    if len(ag_df[ag_df[['Term Code','Course Title', 'Instructor Last Name']].duplicated() == True]) == 0:
        print("From basic tests, the data aggregation is working correctly.")