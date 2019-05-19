# Backend Repo
[![Build
Status](https://travis-ci.com/stev-ou/stev-api.svg?branch=master)](https://travis-ci.com/stev-ou/stev-api)  

## Overview
Included functionality:
- Flask server deployed with Gunicorn
- MongoDB database connection (running on MongoDB atlas)

## Building 

```bash
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

To run debug server locally:

```bash
$ make debug
```

## Running Tests (incl. linting)
```bash
$ make test
```

## Deploying

Currently deploying using Docker.  
Ensure Docker is installed on your machine before continuing.  
Python WSGI application deployed behind Gunicorn.  
Targets included in Makefile.

Manually: 
```bash
$ docker build . -t samjett/ou-reviews-api
$ docker run -p 5051:5050 samjett/ou-reviews-api:latest
$ docker push samjett/ou-reviews-api:latest
```
