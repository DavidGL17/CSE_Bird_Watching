#! /bin/bash
caddy stop
caddy run --config /home/reds/cse/raspberrypi/caddy/Caddyfile
sh /home/reds/cse/raspberrypi/python.sh
