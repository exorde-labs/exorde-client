#!/bin/bash

while true
do
    python3.10 main.py "$@"
    echo "main.py has crashed with exit code $?. Respawning..." >&2
    sleep 1
done
