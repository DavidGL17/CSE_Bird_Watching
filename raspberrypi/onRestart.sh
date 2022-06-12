#! /bin/bash
sleep 20
caddy stop
caddy run --config /home/reds/cse/raspberrypi/caddy/Caddyfile&
sh /home/reds/cse/raspberrypi/python.sh
