# Exorde Participation Module CLI v1.3.1

The full documentation of Exorde Participation Module CLI is available on https://docs.exorde.network.

## Instructions

You have several choices to run the Exorde CLI:

- Run [from sources](#run-from-sources) inside a virtual Python environment
- Run [from a Docker image](#docker)

The Exorde CLI does not come with a GUI, it aims to be used by advanced users who want to run it inside a terminal. The installation process assume that users who run Exorde CLI are familiar with command lines.

The installation process primarly targets Linux distributions. However, most of commands used are the same on macOS and modern Windows system (using a PowerShell console).

Using the container image is the recommanded way to run Exorde CLI, as it avoid dependencies issues, handles automatic restart in case of failure/application update and make multi easier to run multiple instances of the application.

## Requirements

- Windows 8.1/10/11 or Linux or macOS
- 4 GB RAM
- 2 CPU cores
- 1 GB storage (HDD or SSD)

## Quickstart using Python and Conda on Linux/macOS

1.  Follow the [Conda's documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation) to install it on your system.
2.  Download and unzip the latest version of Exorde CLI:
    ```bash
    wget https://github.com/exorde-labs/ExordeModuleCLI/archive/refs/heads/main.zip \
    --output-document=ExordeModuleCLI.zip \
    && unzip ExordeModuleCLI.zip \
    && rm ExordeModuleCLI.zip \
    && mv ExordeModuleCLI-main ExordeModuleCLI
    ```
3.  Go to the root of Exorde CLI folder:
    ```bash
    cd ExordeModuleCLI
    ```
4.  Create and activate a new virtual conda environment with Python 3.9 as the environment executable (exorde-env is an example name):
    ```bash
    conda create --name exorde-env python=3.9
    conda activate exorde-env
    ```
5.  Upgrade Pip :
    ```bash
    pip install --upgrade pip
    ```
6.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
7.  Run the program:

    ```bash
    python Launcher.py -m <YOUR_MAIN_ADDRESS> -l <LOGGING_LEVEL>
    ```

    Usage example:

    ```bash
    python Launcher.py -m 0x0F67059ea5c125104E46B46769184dB6DC405C42 -l 2
    ```

For more detailled informations, please read the [full documentation](https://docs.exorde.network).

## Quickstart using Docker on a Linux VPS

1. Install [Docker](https://docs.docker.com/engine/install/).
2. Run the program in background with autorestart:

   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --name exorde-cli \
   rg.fr-par.scw.cloud/exorde-labs/exorde-cli \
   -m <YOUR_MAIN_ADDRESS> \
   -l <LOGGING_LEVEL>
   ```

   Usage example:

   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --name exorde-cli \
   rg.fr-par.scw.cloud/exorde-labs/exorde-cli \
   -m 0x0F67059ea5c125104E46B46769184dB6DC405C42 \
   -l 2
   ```

For more detailled informations, please read the [full documentation](https://docs.exorde.network).

## When running

For example, if you run in conda mode with -l 2 (moderate amount of logs), you should see this in the console:

```bash
>python Launcher.py -m 0x0000000000000000000000000000000000000001 -l 2
Selected logging > Level: 2 . (0 = no logs, 1 = general logs, 2 = validation logs, 3 =
validation + scraping logs, 4 = detailed validation + scraping logs

[INITIAL MODULE SETUP] Downloading code modules on decentralized
storage...
Code Sub-Module 1 / 4 Downloading... https://bafybeibuxrjwffjeymrjlkd2r35r5rdlzxuavoeympqgr7xrxor6hp3bh4.ipfs.w3s.link/Transaction.py
Code Sub-Module 2 / 4 Downloading... https://bafybeifqnq76utn767m4qbwd4j2jg6k3ypwcr2do7gkk3b26ooxfmzgc5e.ipfs.w3s.link/Scraper.py
Code Sub-Module 3 / 4 Downloading... https://bafybeibbygfm276hjion7ocaoyp3wlfodszhlba6jy3b3fzd37zawkfbgi.ipfs.w3s.link/Validator.py
Code Sub-Module 4 / 4 Downloading... https://bafybeicdgmxvetbi4yqjztzzroevcfvnwobk6zomsz5nh4lvb3dftyimxa.ipfs.w3s.link/App.py

[Init] UPDATING CONFIG [Init] READING CONFIG FILE [Init] Current Config : {'ExordeApp': {'ERCAddress': '', 'MainERCAddress': '', 'Updated': 0, 'SendCountryInfo': 1, 'lastInfo': 'Hello, you are now an Exorder!', 'lastUpdate': '1.3.1'}}
[Init] FIRST WORKER LAUNCH
[Init] New Worker Local Address = 0x4A94c5D4C49597cd889eB569D0Bf4d6e2aC3aE29
[Init] First funding of the worker wallet [Initial Auto Faucet] Top up sFuel & some EXDT to worker address...
[Faucet] selecting Auto-Faucet

...
```

The module is autonomous.

## Spontaneous updates

Sometimes, Exorde Labs needs to push some update in the code. The module will detect it, and kill itself.
This is important for the Exorde Network to remain hommogenous, so older versions have to be killed right away.

When this happens, the module will print a message & shut down. It has to be restarted manually.
