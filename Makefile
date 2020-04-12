dependencies:
	@pip install -U pip poetry
	@poetry install

update:
	@poetry update

test:
	@make check
	@make lint
	@make unit

check:
	@pipenv check

lint:
	@echo "Checking code style ..."
	@pipenv run pylint django_core_api test_app

unit:
	@echo "Running unit tests ..."
	ENV=test pipenv run coverage run test_app/manage.py test --no-input

clean:
	@printf "Deleting build files"
	@rm -rf dist .coverage dist/ django_core_api.egg-info/

publish:
	@make clean
	@printf "\nBuilding & Publishing lib"
	@poetry publish --build
	@make clean

setup:
	@pipenv run python setup.py develop

.PHONY: lint publish clean unit test dependencies setup
