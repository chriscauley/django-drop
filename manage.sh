#!/bin/bash

pushd .
cd testapp
python manage.py $@
popd

