install:
	pip3 install -r requirements.txt
	npm install


generate-directly:
	python3 projectIndexer.py generate --fetch-directly --hide-private --verbose

generate:
	python3 projectIndexer.py generate --hide-private --verbose