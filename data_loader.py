# global/PyPI
import pandas as pd
from mongo import MongoDriver as db_conn
import json
import os
import hashlib
from tqdm import tqdm

# local
from mongo import MongoDriver as db_conn
# aggregate_data.py contains the function to aggregate the data
from data_aggregation import aggregate_data

# Define the name of the database and the name of the collection. Insert each .csv record as a document within the collection
DB_NAME = "reviews-db-v1"
OCR_DB_NAME = 'ocr_db_v1'
ocr_collections = ['reviews']#, 'CoAaS', 'CoA&GS', 'CoCE-DoA', 'MFPCoB', 'MCoEaE', 'JRCoE', 'GCoE', 'WFCoFA', 'HC', 'CoIS', 'GCoJaMC', 'CoPaCS', 'UC', 'CfIaDL', 'EWP', 'R-AF']

# Define the number of packets; Required to upload data in packets to avoid AutoReconnect Error from Mongo
n_splits = 100

### DEBUG - force_update is always true - off in prod
def update_database(force_update=False):
    '''
    Get's the data from the OCR scraped databases in the MongoDB named OCR_DB_NAME, and runs aggregations on this data. Ensures that
    each of these datasets (native, unmodified form and the aggregated form) exist within the DB_NAME Mongo database.
    :inputs:
    force_update: boolean denoting whether an update should be forced if the dataset and its aggregated form already exists in DB_NAME.
    :returns:
    connection: a connection to the mongo db named DB_NAME.
    '''

    # Establish DB connection
    conn = db_conn()

    # Modify the ocr collections to achieve standard column naming form
    for ocr_coll in ocr_collections:
        # Get the data out of the ocr_db
        print('Converting the scraped collection -'+ocr_coll+ '- to pd dataframe.')
        ocr_db = conn.get_db_collection(OCR_DB_NAME, ocr_coll)
        df = pd.DataFrame(list(ocr_db.find()))

        # Define new hash function
        sha224_hash = lambda x: int(hashlib.sha224(x.encode('utf-8')).hexdigest()[:8], 16)

        # Condition the df prior to aggregation
        df = df.drop(['_id'],axis=1, errors = 'ignore').rename(columns ={'Individual Responses':'Responses'})
        df['Instructor ID'] = (df['Instructor First Name']+df['Instructor Last Name']).apply(str).apply(sha224_hash).astype('int32').abs()
        df['course_uuid'] = (df['Subject Code']+df['Course Number'].apply(str)+df['Section Title'].apply(lambda x: x[:-4])).apply(str).apply(sha224_hash).astype('int32').abs().apply(str) 
        df['Question Number'] = df['Question Number'].astype(int)
        df['Term Code'] = df['Term Code'].astype(int)
        # Make sure the First and Last names are in camelcase; i.e. no CHUNG-HAO LEE
        df['Instructor First Name'] = df['Instructor First Name'].apply(str.title)
        df['Instructor Last Name'] = df['Instructor Last Name'].apply(str.title)

        print('Loading '+ocr_coll)
        # If the collection doesnt exist or if the update is forced

        if conn.collection_existence_check(DB_NAME, ocr_coll)==False or force_update:
            collection = conn.get_db_collection(DB_NAME, ocr_coll)

            # Delete all of the current contents from the collection
            collection.delete_many({})
            print(f'Uploading unmodified collection - {ocr_coll} - to {DB_NAME}')

            for i in tqdm(range(n_splits)): # Splits df into n_splits parts
                # load the db for the given data file into a json format
                records = df[(i)*int(len(df)/n_splits):(i+1)*int(len(df)/n_splits)].to_dict('records')
                # try to update the database with the given data file 
                result = collection.insert_many(records)

            # Update the user on what happened
            print('A collection called -' + ocr_coll + '- was added to the database '+ DB_NAME + '.')

        else:
            print('A collection called -' + ocr_coll + '- already exists in the database '+ DB_NAME + ' and was unmodified.')
            
        # Check to see if the aggregated document already exists in the document in the database
        if conn.collection_existence_check(DB_NAME, 'aggregated_' + ocr_coll)==False or force_update:
            collection = conn.get_db_collection(DB_NAME, 'aggregated_' + ocr_coll)

            # Create the aggregated database 
            print('Aggregating the -' + ocr_coll + '- collection. This typically takes 5-10 minutes.')
            ag_df = aggregate_data(df)

            # load the db for the given data file into a json format
            ag_records = json.loads(ag_df.T.to_json()).values()

            # Delete all of the current contents from the collection
            collection.delete_many({})

            # Push the aggregated df to mongo
            print(f'Uploading aggregated collection - aggregated_{ocr_coll}- to {DB_NAME}')
            for i in tqdm(range(n_splits)): # Splits ag_df into n_splits parts
                # load the db for the given data file into a json format
                records = ag_df[(i)*int(len(ag_df)/n_splits):(i+1)*int(len(ag_df)/n_splits)].to_dict('records')
                # try to update the database with the given data file 
                result = collection.insert_many(records)

            # Update the user on what happened
            print('A collection called aggregated_'+ ocr_coll + ' was added to the database '+ DB_NAME + '.')

        else:
            print('A collection called aggregated_'+ ocr_coll + ' already exists in the database '+ DB_NAME + ' and was unmodified.')
            
    # Return the connection to the collection
    return conn
    
if __name__ == '__main__':
    # Update the database
    update_database(force_update=True)