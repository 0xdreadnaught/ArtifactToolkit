#!/bin/sh

# Swap out plceholders with env ports
/etc/nginx/swap_ports.sh

# Run a self test for verbosity's sake
nginx -t

# Launch Nginx
nginx -g 'daemon off;'
