#!/bin/bash

# Function to check if a directory contains a virtual environment
check_virtualenv() {
    if [ -f "$1/bin/activate" ]; then
        return 0
    else
        return 1
    fi
}

# Recursive function to search for a virtual environment
search_virtualenv() {
    local current_dir="$1"

    # Check if the current directory contains a virtual environment
    if check_virtualenv "$current_dir"; then
        echo "Virtual environment found: $current_dir"
        env=$current_dir/bin/activate
        return
    fi

    # Iterate through subdirectories
    for dir in "$current_dir"/*/; do
        if [ -d "$dir" ]; then
            # Recursively search subdirectories
            search_virtualenv "$dir"
        fi
    done
}

# create directory work if missing
WORKDIR="./work"
if [ ! -d $WORKDIR ]; then
    mkdir -p $WORKDIR
fi

# Start searching from the current directory
echo searching for a virtual environment
shopt -s dotglob                #including dotted directories
search_virtualenv .


if [ -z "$env" ]; then
    echo "No virtual environment found in the current directory"
    exit 1
fi


lsof -i :8080 | grep -q "python3"

if [ $? -eq 0 ]; then
    echo "Python3 process is listening on port 8080"
    echo "Killing python3 processes listening on port 8080"
    lsof -i :8080 | grep "python3" | awk '{print $2}' | xargs kill
fi

# Check if linux processes are listening on port 8080
lsof -i :8080 | grep -q "linux"

if [ $? -eq 0 ]; then
    echo "Linux processes are listening on port 8080"
    echo "Killing linux processes listening on port 8080"
    lsof -i :8080 | grep "linux" | awk '{print $2}' | xargs kill
fi

# Check if vde processes are listening on port 8080
lsof -i :8080 | grep -q "vde"

if [ $? -eq 0 ]; then
    echo "Vde processes are listening on port 8080"
    echo "Killing vde processes listening on port 8080"
    lsof -i :8080 | grep "vde" | awk '{print $2}' | xargs kill
fi

echo "Starting backend"
x-terminal-emulator -e bash -c "source $env; cd backend; python3 api.py" &


sleep 5
echo "Starting frontend"
source $env; cd gui; python3 nc_main_wnd.py

