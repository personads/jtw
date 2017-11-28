#!/bin/bash

port=3001
 
while getopts ":p:" opt; do
    case $opt in
        p)
            port=$OPTARG
        ;;
        \?)
            echo "Unknown option: -$OPTARG" >&2
            exit 1
        ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
        ;;
    esac
done

echo "Jesus takes the wheel on port $port"
run/mlp.py -p $port
