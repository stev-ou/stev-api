from flask import Flask, jsonify, request
from flask_cors import CORS
from data_loader import update_database
from mongo import mongo_driver
from bson.json_util import dumps
import pandas as pd
import json
import api_functions as api

# Establish a database connection
DB_NAME = "reviews-db"
COLLECTION_NAME = "reviews-collection"

# base route for this api version
base_api_route = '/api/v0/'

db = mongo_driver()

# PreCompute the instructor and course lists
instructor_list = api.SearchAutocomplete(db, 'instructor')
course_list = api.SearchAutocomplete(db, 'course')

app = Flask(__name__)
CORS(app)

# useful for testing
# curl -i http://localhost:5050/api/v0/

@app.route('/')
def hello_world():
    return 'Ping <a href="/api/v0/">/api/v0/</a> for api'.format(str(request.remote_addr))

@app.route(base_api_route, methods=['GET'])
def root_api():
    return jsonify({'message': 'You have reached api root endpoint. Please see the Github page for information on the endings to hit: https://github.com/stev-ou/stev-api'})

# Search for all entries for autocomplete
@app.route(base_api_route+'<string:search_type>/all')
def course_autocomplete_api(search_type):
    if search_type == 'instructors':
        return jsonify({'result':instructor_list})
    elif search_type =='courses':
        return jsonify({'result':course_list})
    else:
        return jsonify({})

### APIs for Course search
course_suffix_function_map = {'figure1':api.CourseFig1Table, 'figure2':api.CourseFig2Chart, 
'figure3':api.CourseFig3Timeseries, 'figure4':api.CourseFig4TableBar}

@app.route(base_api_route+'courses/<string:course_uuid>/<string:api_suffix>', methods=['GET'])
def course_figure_apis(course_uuid, api_suffix):
    func = course_suffix_function_map[api_suffix]
    response = func(db, course_uuid)
    return jsonify(response)

## APIs for Instructor Search
instr_suffix_function_map = {'figure1':api.InstructorFig1Table, 'figure2':api.InstructorFig2Timeseries, 
'figure3':api.InstructorFig3TableBar, 'chip':api.InstructorChipAPI}

@app.route(base_api_route+'instructors/<int:instructor_id>/<string:api_suffix>', methods=['GET'])
def instructor_figure_apis(instructor_id, api_suffix):
    func = instr_suffix_function_map[api_suffix]
    response = func(db, instructor_id)
    return jsonify(response)

if __name__ == '__main__':
    print("Updating database...")
    # print('IN DEVELOPMENT MODE; NO DATABASE UPDATE PERFORMED')
    # update_database(force_update=False)
    print("Done.")
    print("Starting server listening on port 5050...")
    app.run(host='0.0.0.0', port=5050)
