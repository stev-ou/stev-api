.PHONY: debug
debug:
	env/bin/python server.py

.PHONY: image
image:
	docker build . -t gcr.io/ou-reviews/stev-api

.PHONY: test
test:
	python3 -m unittest discover -v -s tests/
	pylint --errors-only backend

.PHONY: run
run:
	gunicorn -w 4 -b 0.0.0.0:5050 server:app
