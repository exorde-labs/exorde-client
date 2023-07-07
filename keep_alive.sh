#!/bin/bash
while true
do
    exorde "$@"
    exit_code=$?
    echo "exorde has crashed with exit code $exit_code. Respawning..." >&2
    if [ $exit_code -eq 42 ]
    then
        sleep 60
    elif [ $exit_code -eq 0 ]
    then
        sleep 30
    else
        sleep 15
    fi
done
