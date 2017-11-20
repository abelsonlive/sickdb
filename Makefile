
build:
	pip uninstall .
	rm -rf build/ dist/ *.egg-info/
	pip install --editable .
