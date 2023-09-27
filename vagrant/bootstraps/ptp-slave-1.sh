#!/bin/bash

script="ptp-slave-1.sh"
service="ptp-slave-1.service"

sudo cp /vagrant/startups/$script /opt/$script
sudo chmod +x /opt/$script

sudo cp /vagrant/startups/$service /etc/systemd/system/$service
sudo systemctl enable $service
