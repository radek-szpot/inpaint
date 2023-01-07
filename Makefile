init:
	pip install -r requirements.txt

start:
	python __main__.py

test:
	pytest -ra