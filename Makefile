PACKAGE_NAME=groceries


format:
	isort $(PACKAGE_NAME)
	black $(PACKAGE_NAME)

format-tests:
	isort tests
	black tests

format-main:
	isort main_db.py
	black main_db.py

format-all:
	isort $(PACKAGE_NAME)
	isort tests
	black $(PACKAGE_NAME)
	black tests

lint:
	flake8 $(PACKAGE_NAME)
	pylint $(PACKAGE_NAME)

lint-tests:
	flake8 $(PACKAGE_NAME)

tests-cov:
	 pytest --cov-report html --cov=$(PACKAGE_NAME) tests/unit

.PHONY: tests
tests:
	 pytest tests/
