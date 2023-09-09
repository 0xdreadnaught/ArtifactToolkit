#!/bin/sh

# Swap out placeholders with env ports
/etc/nginx/swap_ports.sh

# Run a self test for verbosity's sake
nginx -t

# Find the installed PHP-FPM version and start it
PHP_FPM_VERSION=$(dpkg -l | grep php-fpm | awk '{print $2}' | cut -d':' -f1)
service $PHP_FPM_VERSION start

# Launch Nginx
nginx -g 'daemon off;'

