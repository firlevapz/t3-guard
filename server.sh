#!/bin/bash

dir=`dirname $0`
cd "$dir"

./manage.py runserver 0.0.0.0:9000 --noreload
