PACKAGE_NAME=groceries


format:
	isort $(PACKAGE_NAME)
	black $(PACKAGE_NAME)

format-main:
	isort main.py
	black main.py
	isort main_db.py
	black main_db.py

lint:
	flake8 $(PACKAGE_NAME)
	pylint $(PACKAGE_NAME)
