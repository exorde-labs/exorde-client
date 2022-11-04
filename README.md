
# Exorde Participation Module CLI v1.3.1

[ This is a work in progress ] 
[ only for experienced linux users ]

## Instructions

**The software is written with Python 3.9.**

**Please create a new virtual conda environment with Python 3.9 as the environment executable.**
Activate the environment, then:

Make sure to be at the root of the folder.
**cd ExordeModuleCLI/**
Then install the required packages to run Launcher.py
    pip install -r requirements.txt

**Launch the software with the following example:**

    python Launcher.py -m 0x0F67059ea5c125104E46B46769184dB6DC405C42 -l 2

**Usage: python Launcher.py [-h] -m MAIN_ADDRESS [-l LOGGING]**

 -m MAIN_ADDRESS, --main-address MAIN_ADDRESS
**Main Ethereum Address, which will get all REP & EXDT for this local worker contribution. Exorde Reputation is
 non-transferable.**

 *Correct usage example:*

    -m 0x0F67059ea5c125104E46B46769184dB6DC405C42

  **0x... must be a VALID Ethereum Address (with the checksum format, lower &  uppercase, in case of doubt, copy paste from Etherscan, you must include the 0x prefix)**   

-l,  --logging LOGGING

    level of logging in the console: 0 = no logs, 1 = general logs, 2 = validation logs, 3 = validation + scraping logs, 4 = detailed validation + scraping logs (e.g. for troubleshooting)


**Some packages might be missing, you can install then with pip: (it might be needed if your pip version is broken/outdated, etc)**

pip install eth-account fasttext-langdetect facebook_scraper
pip install geopy iso369 Pillow
pip install apache-libcloud
pip install ...

## When running

For example, if you run Launcher.py it with -l 2 (moderate amount of logs), you should see this in the console:

> (my_env) \...\user\ExordeModuleCLI>python Launcher.py -m 0x0000000000000000000000000000000000000001 -l 2 
> 
> Selected logging > Level:  2 .  (0 = no logs, 1 = general logs, 2 = validation logs, 3 =
> validation + scraping logs, 4 = detailed validation + scraping logs
> 
> [INITIAL MODULE SETUP] Downloading code modules on decentralized
> storage...
>         Code Sub-Module  1  /  4        Downloading...   https://bafybeibuxrjwffjeymrjlkd2r35r5rdlzxuavoeympqgr7xrxor6hp3bh4.ipfs.w3s.link/Transaction.py
>         Code Sub-Module  2  /  4        Downloading...   https://bafybeifqnq76utn767m4qbwd4j2jg6k3ypwcr2do7gkk3b26ooxfmzgc5e.ipfs.w3s.link/Scraper.py
>         Code Sub-Module  3  /  4        Downloading...   https://bafybeibbygfm276hjion7ocaoyp3wlfodszhlba6jy3b3fzd37zawkfbgi.ipfs.w3s.link/Validator.py
>         Code Sub-Module  4  /  4        Downloading...   https://bafybeicdgmxvetbi4yqjztzzroevcfvnwobk6zomsz5nh4lvb3dftyimxa.ipfs.w3s.link/App.py
> 
> [Init] UPDATING CONFIG [Init] READING CONFIG FILE [Init] Current Config :  {'ExordeApp': {'ERCAddress': '', 'MainERCAddress': '',  'Updated': 0, 'SendCountryInfo': 1, 'lastInfo': 'Hello, you are now an
> Exorder!', 'lastUpdate': '1.3.1'}}
>  [Init] FIRST WORKER LAUNCH
>  [Init] New Worker Local Address =  0x4A94c5D4C49597cd889eB569D0Bf4d6e2aC3aE29
> [Init] First funding of the worker wallet [Initial Auto Faucet] Top up
> sFuel & some EXDT to worker address... 
> [Faucet] selecting Auto-Faucet ...

The module is autonomous.

## Spontaneous updates

Sometimes, Exorde Labs needs to push some update in the code. The module will detect it, and kill itself.
You then have to run it again. This is important for the Exorde Network to remain hommogenous, so older versions have to be killed right away.

When this happens, the module will print a message & shut down.
