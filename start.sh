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
if [ -f ./jesus.state ]; then
    rm ./jesus.state
    echo "Removed Jesus State File"
fi
python3 run/mlp.py -p $port
