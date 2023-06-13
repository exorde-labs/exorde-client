# Exorde Participation Module

The full documentation of Exorde Participation Module is available on https://docs.exorde.network.

## Instructions

You have several choices to run the Exorde CLI:

- Run from sources inside a virtual Python environment
- Run from a Docker image (RECOMMENDED)

Exorde client does not come with a GUI, it aims to be used by advanced users who want to run it inside a terminal. The installation process assume that users who run Exorde CLI are familiar with command lines.

Using the container image is the recommanded way to run Exorde CLI, as it avoid dependencies issues, handles automatic restart in case of failure/application update and make multi easier to run multiple instances of the application.

## Requirements

- Windows 8.1/10/11 or Linux or macOS
- 6 GB RAM per instance/container
- 2-4 virtual CPU cores (4 recommended)
- 40 GB storage (HDD or SSD) (the image is currently 30 gb)
- Python 3.10
- no GPU required

## Quickstart using Python and Conda on Linux/macOS (DEPRECATED, to update)

1.  Follow the [Conda's documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation) to install it on your system.
2.  Download and unzip the latest version of Exorde CLI:
    ```bash
    wget https://github.com/exorde-labs/exorde-client/archive/refs/heads/main.zip \
    --output-document=exorde-client.zip \
    && unzip exorde-client.zip \
    && rm exorde-client.zip \
    && mv exorde-client-main exorde-client
    ```
3.  Go to the root of Exorde CLI folder:
    ```bash
    cd exorde-client
    ```
4.  Create and activate a new virtual conda environment with Python 3.9 as the environment executable (exorde-env is an example name):
    ```bash
    conda create --name exorde-env python=3.10
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
    python ./exorde/main.py --main_address <YOUR_MAIN_ADDRESS>
    ```

    Usage example:

    ```bash
    python ./exorde/main.py -m 0x0F67059ea5c125104E46B46769184dB6DC405C42
    ```

For more detailled informations, please read the [full documentation](https://docs.exorde.network).

## Quickstart using Docker on a Linux VPS

1. Install [Docker](https://docs.docker.com/engine/install/).
2. Run the program in background with autorestart:

   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --pull always \
   --name <CONTAINER_NAME> \
   exordelabs/exorde-client \
   -m <YOUR_MAIN_ADDRESS> \
   -l <LOGGING_LEVEL>
   ```

   Usage example:

   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --pull always \
   --name exorde-client \
   exordelabs/exorde-client \
   -m 0x0F67059ea5c125104E46B46769184dB6DC405C42
   ```
   
2. Run multiple containers on same machine, and limit their machine usage with arguments --cpus="x" --memory="Xg"

   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --cpus="x" --memory="Xg" \
   --pull always \
   --name <CONTAINER_NAME> \
   exordelabs/exorde-client \
   -m <YOUR_MAIN_ADDRESS> \
   -l <LOGGING_LEVEL>
   ```

   Usage example:

   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --cpus="4" --memory="6g" \
   --pull always \
   --name exorde-client \
   exordelabs/exorde-client \
   -m 0x0F67059ea5c125104E46B46769184dB6DC405C42
   ```
    

For more detailled informations, please read the [full documentation](https://docs.exorde.network).

## How to update the Docker image:

**Note: Exorde CLI has an auto update mechanism, there is no need to pull a new Docker image. Script files inside the container are updated regularly. Pull a new image is useful only if the auto update fails.**

If you are already running Exorde CLI with Docker and you want to use a new uploaded image, please follow these instructions:

1. Stop and delete all running containers of Exorde CLI:

   ```
   docker stop <CONTAINER_NAME> && docker rm <CONTAINER_NAME>
   ```

   For example, if you are running only one container named "exorde-cli":

   ```
   docker stop exorde-client && docker rm exorde-client
   ```

2. Start new containers:
   ```bash
   docker run \
   -d \
   --restart unless-stopped \
   --pull always \
   --name <CONTAINER_NAME> \
   exordelabs/exorde-client \
   -m <YOUR_MAIN_ADDRESS> \
   -l <LOGGING_LEVEL>
   ```

## When running

For example, if you run in conda mode with `-l 2` (moderate amount of logs), you should see this in the console:

> ⚠ This output is outdated, it will be replaced soon. ⚠

```bash
$ python Launcher.py -m 0x0000000000000000000000000000000000000001 -l 2
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

The module is autonomous. It is made to be plugin-based for scrapers, so feel free to submit your scrapers, part of Exorde Labs's Open Source bounty program (to properly develop in 2023).

## Spontaneous updates

Sometimes, Exorde Labs needs to push some update in the code. The module will detect it, and kill itself.
This is important for the Exorde Network to remain hommogenous, so older versions have to be killed right away.

When this happens, the module will print a message & shut down. It has to be restarted manually.
