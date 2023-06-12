venv:
	rm -rf env
	python3 -m virtualenv env
	env/bin/pip3 install -e ./data
	env/bin/pip3 install -e ./data/scraping/reddit
	env/bin/pip3 install -e ./data/scraping/twitter
	env/bin/pip3 install -e ./data/scraping/4chan
	env/bin/pip3 install -e ./exorde
	env/bin/pip3 install --upgrade git+https://github.com/JustAnotherArchivist/snscrape.git

protocol_schema:
	rm -rf exorde/exorde/schema.json
	env/bin/python3 exorde/exorde/protocol/__init__.py >> exorde/exorde/schema.json
	cat exorde/exorde/schema.json

_lab:
	docker build -t exorde_lab lab

_data:
	docker build -t data data

_client:
	docker built -t exorde exorde

image: _lab _data _client

run:
	docker run exorde
