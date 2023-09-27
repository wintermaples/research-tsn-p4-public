#!/bin/bash

script="ptp-master.sh"
service="ptp-master.service"

sudo cp /vagrant/startups/$script /opt/$script
sudo chmod +x /opt/$script

sudo cp /vagrant/startups/$service /etc/systemd/system/$service
sudo systemctl enable $service
