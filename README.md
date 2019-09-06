# STEV Backend
[![Build
Status](https://travis-ci.com/stev-ou/stev-api.svg?branch=master)](https://travis-ci.com/stev-ou/stev-api)  
Student-Teacher Evaluation Visualization (**STEV**, pronounced "Steve")  

A project to create a better data visualization for anonymous student reviews of
professors/courses/departments at the University of Oklahoma. The reviews are
currently available in individual, non-queryable pdfs (a collection of thousands
of pdfs) at the following website -
http://www.ou.edu/provost/course-evaluation-data. We created a data
visualization to present this information and make it accessible to students.  

The backend creates a WSGI webserver behind Green Unicorn to provide the data to
the frontend. The backend api is accessible via a public URL, as described below.

## Backend Endpoints
The api is available at [https://api.evals.info/api/v0/](https://api.evals.info/api/v0/). The specific endpoints are accessed through a schema setup in the [**API Usage**](#api-usage) section. Some brief examples are shown below.

_**Course Examples**_

https://api.evals.info/api/v0/courses/all     (list all courses)

https://api.evals.info/api/v0/courses/1540998145/figure1  (General Chemistry)

https://api.evals.info/api/v0/courses/508260345/figure3    (Financial Accounting)

https://api.evals.info/api/v0/courses/1050273945/figure4   (Advanced Machine Learning)

_**Instructor Examples**_

https://api.evals.info/api/v0/instructors/all   (list all instructors)

https://api.evals.info/api/v0/instructors/941452360/figure1  (Dr. Walker Womack)

https://api.evals.info/api/v0/instructors/1880901448/figure2  (Dr. Rachel Childers)

https://api.evals.info/api/v0/instructors/1727379373/figure3   (President David Boren)


## API Usage
We currently have an open API for accessing the information about the courses and reviews in a JSON format. You can access the API root, or base, at:

https://api.evals.info/api/v0/

To query data from the API, you just append the appropriate string to the api. Currently, the api is built out to serve data for the figures in the frontend, but this could easily be modified to serve desired data in an arbitrary format. Please contact [the STEV team](contact@evals.info) if you would like to discuss using this data or building out another project based on the evaluation data.

**Search By Course**:
To obtain a JSON object with the names and Course IDs of all courses, append the string `courses/all` to the root api. Then, you can search through this to find the code of the course you are interested in. To obtain data for a specific course, append `courses/{hashed_course_ID}/{api suffix}` to the API string. Courses are hashed into integer values, which can be obtained from `courses/all` endpoint. So for the course CS5043: Advanced Machine Learning, we will obtain its hashed ID - 1050273945 - then append this to the root and add a suffix from the list - *figure1*, *figure2*, *figure3*, or *figure4*.

**Example:** Full URL address for Numerical Methods api (e.g., Figure 1):

https://api.evals.info/api/v0/courses/1050273945/figure1

**Search By Instructor**:
To obtain an object with the names and (hashed) IDs of each instructor, append the string `instructors/all` to the api. Then, you can search through this to find hashed ID of the instructor you are interested in. To obtain data for a specific instructor, append `instructors/{instructor hashed ID}/{api suffix}` to the API string. Optional suffixes for the instructors api include - *figure1*, *figure2*, *figure3*, and *chip*. For example, if we want to obtain data for Dr. Chad Davis, we first append `instructors/all` to the root api string and search for Chad Davis to find his hashed ID (1017823331), then append `instructors/1017823331` to the root, and finally add a desired suffix to the end of the string to get the data for the figures for this instructor.

**Example:** Full URL address for Dr. Chad Davis api (e.g., Figure 2):

https://api.evals.info/api/v0/instructors/1017823331/figure1

## Building 
In order to build and run the application, ensure `python 3.6` and `GNU Make`
are installed. The instructions here assume your Python interpreter is available
via the `python3` binary.   

After cloning the repository, change directory into `stev-api` and run:

```bash
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

To run debug server locally:

```bash
$ make debug
```

## Running Tests (includes linting)
```bash
$ make test
```
