#!/bin/sh

if [ ! -f /etc/nginx/certs/nginx.crt ]; then
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/certs/nginx.key -out /etc/nginx/certs/nginx.crt -subj 
'/CN=localhost'
fi

nginx -g 'daemon off;'
