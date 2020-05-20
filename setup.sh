#!/bin/bash

sudo ln -s "$HOME/dotjellies/nginx/conf.d/jellyfin.conf" "/etc/nginx/conf.d/jellyfin.conf"
sudo ln -s "$HOME/dotjellies/nginx/conf.d/jstat.conf" "/etc/nginx/conf.d/jstat.conf"
sudo ln -s "$HOME/dotjellies/systemd/system/certbot.service" "/etc/systemd/system/certbot.service"
sudo ln -s "$HOME/dotjellies/systemd/system/certbot.timer" "/etc/systemd/system/certbot.timer"
sudo ln -s "$HOME/dotjellies/systemd/system/jstat.service" "/etc/systemd/system/jstat.service"
sudo ln -s "$HOME/dotjellies/systemd/system/rpistats.service" "/etc/systemd/system/rpistats.service"
sudo ln -s "$HOME/dotjellies/systemd/system/rpistats.timer" "/etc/systemd/system/rpistats.timer"

mkdir -p "$HOME/dotjellies/jstat/data"

sudo systemctl enable certbot.timer
sudo systemctl enable rpistats.timer
sudo systemctl enable jstat.service