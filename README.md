# Backend Repo

[![Build Status](https://travis-ci.com/samjett247/OU-Student-Reviews-DB.svg?token=SVpA8x2aEJENtpVkhC28&branch=master)](https://travis-ci.com/samjett247/OU-Student-Reviews-DB)

Website is available [here](http://35.193.175.5).  

Api backend is available here [here](http://35.188.130.122/api/v0).  

Included functionality:
- Flask server
- MongoDB interface
- Tests
- need to add more

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
```bash
$ docker build . -t samjett/ou-reviews-api
$ docker run -p 5051:5050 samjett/ou-reviews-api:latest
$ docker push samjett/ou-reviews-api:latest
```
