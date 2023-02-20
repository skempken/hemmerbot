#!/bin/bash

rm -rf python/*

source ../lambda-functions/venv/bin/activate
pip3 install -r ../lambda-functions/requirements.txt -t ./python
deactivate