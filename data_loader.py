# global/PyPI
import pandas as pd
import json
import os
import hashlib

# local
from mongo import mongo_driver as db_conn
# aggregate_data.py contains the function to aggregate the data
from data_aggregation import aggregate_data

# Define the name of the database and the name of the collection. Insert each .csv record as a document within the collection
DB_NAME = "test-agg-db" # practice
OCR_DB_NAME = 'ocr_db_v1'
ocr_collections = ['CoA']#, 'CoAaS', 'CoA&GS', 'CoCE-DoA', 'MFPCoB', 'MCoEaE', 'JRCoE', 'GCoE', 'WFCoFA', 'HC', 'CoIS', 'GCoJaMC', 'CoPaCS', 'UC', 'CfIaDL', 'EWP', 'R-AF']

### DEBUG - force_update is always true - off in prod
def update_database(force_update=False):
    '''
    Get's the csv data from the OCR scraped databases in the MongoDB named OCR_DB_NAME, and runs aggregations on this data. Ensures that
    each of these datasets (native, unmodified form and the aggregated form) exist within the DB_NAME Mongo database.
    :inputs:
    force_update: boolean denoting whether an update should be forced if the dataset and its aggregated form already exists in DB_NAME.
    :returns:
    connection: a connection to the mongo db named DB_NAME.
    '''

    # Establish DB connection
    conn = db_conn()

    db_dfs = {}

    # Modify the ocr collections to achieve standard column naming form
    for ocr_coll in ocr_collections:
        print('Converting the scraped collection '+ocr_coll+ ' to pd dataframe.')
        ocr_db = conn.get_db_collection(OCR_DB_NAME, ocr_coll)
        df = pd.DataFrame(list(ocr_db.find()))
        df.drop(['_id'],axis=1, inplace=True).rename(columns ={'Individual Responses':'Responses'}, inplace=True)
        df['Instructor ID'] = (df['Instructor First Name']+df['Instructor Last Name']).apply(str).apply(hash).astype('int32').abs()
        # Make sure the First and Last names are in camelcase; i.e. no CHUNG-HAO LEE
        df['Instructor First Name'] = df['Instructor First Name'].apply(str.title)
        df['Instructor Last Name'] = df['Instructor Last Name'].apply(str.title)
        ## Undo the below lines to get a list of the unique question numbers for OCR
        print(ocr_coll)
        mylist = sorted(df['Question Number'].unique())
        print(mylist)
        print('\n')


        db_dfs[ocr_coll] = df # Create a df and add it to the dict

    for df_name in db_dfs.keys():
        print('Loading '+df_name)
        # If the collection doesnt exist or if the update is forced

        if conn.collection_existence_check(DB_NAME, df_name)==False or force_update:
            collection = conn.get_db_collection(DB_NAME, df_name)

            # Get the dataframe
            df = db_dfs[df_name]

            # Delete all of the current contents from the collection
            collection.delete_many({})
            if df_name == 'CAaS':
                for i in [1,2,3,4]: # Splits df into 4 parts for uploading without AutoReconnect Error, especially for 
                    # load the db for the given data file into a json format
                    records = df[(i-1)*int(len(df)/4):i*int(len(df)/4)].to_dict('records')
                    # try to update the database with the given data file 
                    result = collection.insert_many(records)
            else:
                records = df.to_dict('records')
                # try to update the database with the given data file 
                result = collection.insert_many(records)

            # Update the user on what happened
            print('A collection called ' + df_name + ' was added to the database '+ DB_NAME + '.')

        else:
            print('A collection called ' + df_name + ' already exists in the database '+ DB_NAME + ' and was unmodified.')
            
        # Check to see if the aggregated document already exists in the document in the database
        if conn.collection_existence_check(DB_NAME, 'aggregated_' + df_name)==False or force_update:
            collection = conn.get_db_collection(DB_NAME, 'aggregated_' + df_name)
            # Get the dataframe
            df = db_dfs[df_name]

            # Create the aggregated database 
            print('Aggregating the ' + df_name + '. This usually takes approximately 1 minute, though can take longer for large datasets.')
            ag_df = aggregate_data(df)

            # load the db for the given data file into a json format
            ag_records = json.loads(ag_df.T.to_json()).values()

            # Delete all of the current contents from the collection
            collection.delete_many({})

            # Try to update the aggregated dataframe
            ag_result = collection.insert_many(ag_records)

            # Update the user on what happened
            print('A collection called aggregated_'+ df_name + ' was added to the database '+ DB_NAME + '.')

        else:
            print('A collection called aggregated_'+ df_name + ' already exists in the database '+ DB_NAME + ' and was unmodified.')
            
    # Return the connection to the collection
    return conn
    
if __name__ == '__main__':
    # Update the database
    update_database(force_update=True)



    
