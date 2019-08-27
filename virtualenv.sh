#!/bin/bash -xe
# bootstrap virtualenv
export VIRTUAL_ENV=.virtualenv/krakenex
mkdir -p $VIRTUAL_ENV
virtualenv $VIRTUAL_ENV
source $VIRTUAL_ENV/bin/activate
$VIRTUAL_ENV/bin/pip install -r requirements.txt

