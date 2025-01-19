install:
	pip3 install -r requirements.txt
	npm install

fetch-github:
	python3 projectIndexer.py fetch-github --verbose

generate-directly:
	python3 projectIndexer.py generate --fetch-directly --hide-private --compile-tailwind --verbose

generate:
	python3 projectIndexer.py generate --hide-private --compile-tailwind --verbose

serve:
	python3 projectIndexer.py serve --host 0.0.0.0

serve-no-livereload:
	python3 projectIndexer.py serve --no-livereload --host 0.0.0.0
