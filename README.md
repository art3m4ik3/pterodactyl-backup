# Pterodactyl backup

## Description
Pterodactyl backup is a simple utility for automatic backup once a day (at 4:00 AM).

## Features
* Built-in CRON similarity
* Asynchronous backups
* Client api pterodactyl

## Installation

Copy .env.example and edit him
```shell
cp .env.example .env
nano .env # or via your favorite editor
```
Install modules:
```shell
python3 -m pip install -r requirements.txt
```
Start:
```shell
python3 main.py
```
