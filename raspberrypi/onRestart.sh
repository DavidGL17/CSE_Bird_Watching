#! /bin/bash
caddy stop
caddy run --config /home/reds/cse/raspberrypi/caddy/Caddyfile
python3 /home/reds/cse/raspberrypi/main.py