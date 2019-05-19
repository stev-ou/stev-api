# STEV Backend
[![Build
Status](https://travis-ci.com/stev-ou/stev-api.svg?branch=master)](https://travis-ci.com/stev-ou/stev-api)  
Student-Teacher Evaluation Visualization -> "Steve"  

A project to create a better data visualization for anonymous student reviews of
professors/courses/departments at the University of Oklahoma. The reviews are
currently available in individual, non-queryable pdfs (a collection of thousands
of pdfs) at the following website -
http://www.ou.edu/provost/course-evaluation-data. We want to create a data
visualization to present this information and make it accessible to students.  

The backend creates a WSGI webserver behind Green Unicorn to provide the data to
the frontend. It is also accessible via a public URL. 

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

## Running Tests (including linting)
```bash
$ make test
```
