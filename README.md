# Exorde Participation Module CLI v1.3.1

[ This is a work in progress ] 
[ only for experienced linux users ]

## Instructions

The software is written with Python 3.9.
Please create a new virtual conda environment.
Activate the environment, then:

cd ExordeModuleCLI/

pip install -r requirements.txt

Launch the software with the following example:

python Launcher.py -m 0x..... -l 2 

usage: Launcher.py [-h] -m MAIN_ADDRESS [-l LOGGING]

optional arguments:
  -h, --help            show this help message and exit
  -m MAIN_ADDRESS, --main-address MAIN_ADDRESS
                        Main Ethereum Address, which will get all REP & EXDT for this local worker contribution. Exorde Reputation is non-transferable. 
                        Correct usage example:
                        -m 0x0F67059ea5c125104E46B46769184dB6DC405C42, must be a VALID Ethereum Address (with the checksum format, lower & uppercase, in case of doubt, copy paste from Etherscan)
  -l LOGGING, --logging LOGGING
                        level of logging in the console: 0 = no logs, 1 = general logs, 2 = validation logs, 3 = validation + scraping logs, 4 = detailed validation + scraping
                        logs (e.g. for troubleshooting)


some packages might be missing, you can install then with pip: (it might be needed if your pip version is broken/outdated, etc)

pip install eth-account fasttext-langdetect facebook_scraper
pip install geopy iso369 Pillow
pip install apache-libcloud
pip install ...

