#!/bin/bash

sudo ln -s "$HOME/dotjellies/nginx/conf.d/jellyfin.conf" "/etc/nginx/conf.d/jellyfin.conf"
sudo ln -s "$HOME/dotjellies/nginx/conf.d/jstat.conf" "/etc/nginx/conf.d/jstat.conf"
sudo ln -s "$HOME/dotjellies/systemd/system/certbot.service" "/etc/systemd/system/certbot.service"
sudo ln -s "$HOME/dotjellies/systemd/system/certbot.timer" "/etc/systemd/system/certbot.timer"
sudo ln -s "$HOME/dotjellies/systemd/system/jstat.service" "/etc/systemd/system/jstat.service"

