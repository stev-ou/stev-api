import pandas as pd
from mongo import mongo_driver as db_conn
import json
import os

# aggregate_data.py contains the function to aggregate the data
from data_aggregation import aggregate_data

# Define the name of the database and the name of the collection. Insert each .csv record as a document within the collection
DB_NAME = "reviews-db"
OCR_DB_NAME = 'ocr_db'
ocr_collections = ['ARC', 'BUS', 'FARTS', 'GEO', 'INTS', 'JRNL', 'NRG']

### DEBUG - force_update is always true - off in prod
def update_database(force_update=False):
    '''
    Loads new data into the database, from the data folder. Each new .csv file is inserted into the database as a new collection. When inserting,
    the only check is to see if a collection with the name of the csv already exists in the database(i.e., if COE_Spring_2018 already exists in 
    the database, it is not inserted or modified. Else, it is inserted). Therefore, once the .csv files are placed into the data folder, do not 
    modify their contents, as the updates will not natively make it to the database.
    :inputs:
    connection: a connection to a collection within the DB
    :returns:
    connection: the same connection to the same collection of documents within the DB (the document set of the collection may be modified)
    '''

    # Establish DB connection
    conn = db_conn()
        
    # Gets the list of data documents to be checked and potentially inserted. Removes non csv files
    data_files = os.listdir('data/')

    db_dfs = {}
    # TEMPORARY COMMENT OUT
    for file in data_files: 
        # Inform about non csv files
        if file[-4:] != '.csv':
            print('The file ' + file + ' is located in the data/ directory, but cannot be uploaded to the DB, because it is not a .csv')
            data_files.remove(file)
        # Convert the relevant .csv data files to df and put into db_df_list
        else:
            print('Converting the file ' + file + ' to pd dataframe.')
            # Reading data into python from the csv
            df = pd.read_csv('data/'+file)
            # Hash the Instructor ID value 
            df['Instructor ID'] = df['Instructor 1 ID'].apply(hash)
            # Make sure the First and Last names are in camelcase; i.e. no CHUNG-HAO LEE
            df['Instructor 1 First Name'] = df['Instructor 1 First Name'].apply(str.title)
            df['Instructor 1 Last Name'] = df['Instructor 1 Last Name'].apply(str.title)
            ## Undo the below lines to get a list of the unique question numbers for OCR
            # print(file)
            # mylist = df['Question Number'].unique()
            # mylist.sort()
            # print(mylist)
            # print('\n')
            # Add to dfs to be inserted into db
            db_dfs[file[:-4]] = df

    # Add OCR collections to the db_dfs
    for ocr_coll in ocr_collections:
        print('Converting the scraped collection '+ocr_coll+ ' to pd dataframe.')
        ocr_db = conn.get_db_collection(OCR_DB_NAME, ocr_coll)
        df = pd.DataFrame(list(ocr_db.find()))
        df.drop(['_id'],axis=1, inplace=True)
        # TEMPORARY WORKAROUND until Joe gets the number of responses scraped
        df['Responses'] = 10
        #####################
        df['Instructor ID'] = (df['Instructor First Name']+df['Instructor Last Name']).apply(hash)
        # Make sure the First and Last names are in camelcase; i.e. no CHUNG-HAO LEE
        df['Instructor First Name'] = df['Instructor First Name'].apply(str.title)
        df['Instructor Last Name'] = df['Instructor Last Name'].apply(str.title)
        ## Undo the below lines to get a list of the unique question numbers for OCR
        # print(ocr_coll)
        # mylist = df['Question Number'].unique()
        # mylist.sort()
        # print(mylist)
        # print('\n')
        
        db_dfs[ocr_coll] = df # Create a df and add it to the dict

    for df_name in db_dfs.keys():
        print('Loading '+df_name)
        # If the collection doesnt exist or if the update is forced
        if conn.collection_existence_check(DB_NAME, df_name)==False or force_update:
            collection = conn.get_db_collection(DB_NAME, df_name )

            # Delete all of the current contents from the collection
            collection.delete_many({})

            # Get the dataframe
            df = db_dfs[df_name]

            # load the db for the given data file into a json format
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
            # Delete all of the current contents from the collection
            collection.delete_many({})
            # Get the dataframe
            df = db_dfs[df_name]

            # Create the aggregated database 
            print('Aggregating the ' + df_name + '. This usually takes about a minute.')
            ag_df = aggregate_data(df)

            # load the db for the given data file into a json format
            ag_records = json.loads(ag_df.T.to_json()).values()

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



    
