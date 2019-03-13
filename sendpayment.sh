#!/bin/bash

now=$(date +"%T")
touch /home/vagrant/crontest/$now

cd /home/vagrant/src/project
source env/bin/activate
source secrets.sh
python sendpayment.py
