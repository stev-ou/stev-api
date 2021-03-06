FROM python:3.7-slim-stretch
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD gunicorn -w 1 -b 0.0.0.0:8080 server:app
