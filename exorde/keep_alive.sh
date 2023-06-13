#!/bin/bash
while true
do
    python main.py "$@"
    exit_code=$?
    echo "main.py has crashed with exit code $exit_code. Respawning..." >&2
    if [ $exit_code -eq 42 ]
    then
        sleep 120
    elif [ $exit_code -eq 0 ]
    then
        sleep 60
    else
        sleep 15
    fi
done
