#!/bin/sh
cd ../streetview
python manage.py sqlreset ratestreets | mysql -u streetview -p streetview
cd ../data
