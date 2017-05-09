#!/bin/bash

sudo apt-get install python3-tk virtualenv matplotlib

virtualenv -p /usr/bin/python3.5 env

source env/bin/activate

pip install -U pip setuptools
pip install requeriments.txt
