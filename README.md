
# Exorde Participation Module CLI v1.3.1

[ This is a work in progress ] 

## Instructions
You have two choices to run the Exorde CLI : 
- create a **Conda** virtual environment: [conda guide](#conda)
- use **Docker** to build and run a container: [docker guide](#docker)

## Conda

**The software is written with Python 3.9.**

### Install

**Please create a new virtual conda environment with Python 3.9 as the environment executable. (exorde-env is an example name)**

    conda create --name exorde-env python=3.9
 

Activate the environment:

    conda activate exorde-env

Upgrade Pip, On Windows the recommended command is:

    python -m pip install --upgrade pip
    
On Ubuntu/Linux distributions:

    pip install --upgrade pip

Make sure to be at the root of the folder:

    cd ExordeModuleCLI

Then install the required packages to run Launcher.py:

    pip install -r requirements.txt

This should install all the packages. The Launcher.py is now ready to be launched with the right arguments (your main Ethereum wallet address & level of logging)

### Run

Run the program:

    python Launcher.py -m YOUR_MAIN_ADDRESS -l LOGGING

 *Usage example:* 

    python Launcher.py -m 0x0F67059ea5c125104E46B46769184dB6DC405C42 -l 2

For more informations about command-line arguments go to [arguments section.](#command-line-arguments) 

 **Some packages might be missing, you can install then with pip: (it might be needed if your pip version is broken/outdated, etc)**

    pip install eth-account fasttext-langdetect facebook_scraper
    pip install geopy iso369

## Docker  

### Docker install
First you need to have Docker installed on your machine. 

You can install Docker server or docker desktop [here.](https://docs.docker.com/engine/install/)

Check you have docker correctly installed by typing on your terminal: 

    docker --version

If it's the case you'll have something like that in output:  

    Docker version 20.10.20, build 9fdeb9c

### Build
You have to build the docker image only once, then you can skip this step and go directly to next section.

Clone the github repository:

    git clone https://github.com/exorde-labs/ExordeModuleCLI.git

Make sure to be at the root of the folder:

    cd ExordeModuleCLI

Build the docker image once (this may take some time depending on your internet connection):

    docker build -t exorde-cli . 

### Run in detached mode (for Virtual Private Servers)
Detached mode allows you to run the program in background so if you deploy it on a VPS you can exit your session and the program will continue to run.

Run the program: 

    docker run -d -e PYTHONUNBUFFERED=1 exorde-cli -m YOUR_MAIN_ADDRESS -l LOGGING


*Usage example:* 

    docker run -d -e PYTHONUNBUFFERED=1 exorde-cli -m 0x0F67059ea5c125104E46B46769184dB6DC405C42 -l 2

For more informations about command-line arguments go to [arguments section.](#command-line-arguments) 


**To get the logs of your container running in background:**

First get the containers currently running
    
    docker ps 

Take the output of the previous command and enter
    
    docker logs --follow <container_id> 


### Run in interactive mode (for local machines)
Interactive mode allows you to stop the program easily with CTRL + C

Run the program: 

    docker run -it exorde-cli -m YOUR_MAIN_ADDRESS -l LOGGING

*Usage example:* 

    docker run -it exorde-cli -m 0x0F67059ea5c125104E46B46769184dB6DC405C42 -l 2

For more informations about command-line arguments go to [arguments section.](#command-line-arguments) 

## Command Line arguments
This section gives you all the arguments you can pass to the command line.

### Main address
**Main Ethereum Address, which will get all REP & EXDT for this local worker contribution.**
**Exorde Reputation is non-transferable.**

> -m MAIN_ADDRESS, --main-address MAIN_ADDRESS

 *Correct usage examples:*

    -m 0x0F67059ea5c125104E46B46769184dB6DC405C42
or 
    
    --main-address=0x0F67059ea5c125104E46B46769184dB6DC405C42

  **0x... must be a VALID Ethereum Address (with the checksum format, lower &  uppercase, in case of doubt, copy paste from Etherscan, you must include the 0x prefix)**  

### Logging 
**Level of logging wanted in console output.** 

> -l,  --logging LOGGING

Possible values: 
- 0 = no logs, 
- 1 = general logs
- 2 = validation logs
- 3 = validation + scraping logs
- 4 = detailed validation + scraping logs (e.g. for troubleshooting)

*Correct usage examples:*

    -l 2
or
    
    --logging=2

### Help 
**Help command to see all arguments.** 

> -h,  --help

*Correct usage examples:*

    -h
or
    
    --help

## When running

For example, if you run in conda mode with -l 2 (moderate amount of logs), you should see this in the console:

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
> 
>  [Init] FIRST WORKER LAUNCH
>  
>  [Init] New Worker Local Address =  0x4A94c5D4C49597cd889eB569D0Bf4d6e2aC3aE29

> [Init] First funding of the worker wallet [Initial Auto Faucet] Top up

> sFuel & some EXDT to worker address... 

> [Faucet] selecting Auto-Faucet ...

The module is autonomous.

## Spontaneous updates

Sometimes, Exorde Labs needs to push some update in the code. The module will detect it, and kill itself.
This is important for the Exorde Network to remain hommogenous, so older versions have to be killed right away.

When this happens, the module will print a message & shut down.
