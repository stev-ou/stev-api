all: install test debug

.PHONY: install
install:
	python3 -m venv env
	env/bin/pip install -r requirements.txt

.PHONY: debug
debug:
	env/bin/python server.py

.PHONY: image
image:
	docker build . -t gcr.io/ou-reviews/stev-api

.PHONY: test
test:
	env/bin/python -m unittest discover -v -s tests/
	pylint --errors-only .

.PHONY: run
run:
	gunicorn -w 4 -b 0.0.0.0:5050 server:app
