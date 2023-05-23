venv:
	rm -rf env
	python3 -m virtualenv env
	env/bin/pip3 install -e ./data
	env/bin/pip3 install -e ./data/scraping/reddit
	env/bin/pip3 install -e ./data/scraping/twitter
	env/bin/pip3 install -e ./lab
	env/bin/pip3 install -e ./exorde
