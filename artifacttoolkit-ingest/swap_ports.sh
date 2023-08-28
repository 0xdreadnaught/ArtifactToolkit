#!/bin/bash

# Replace the INGEST_HTTPS value in default.conf
sed -i "s/REPLACEINGESTPORT/$INGEST_HTTPS/g" /etc/nginx/conf.d/default.conf
