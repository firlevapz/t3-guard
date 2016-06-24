#!/bin/bash

dir=`dirname $0`
cd "$dir"

./manage.py runserver 0.0.0.0:8000 --noreload
