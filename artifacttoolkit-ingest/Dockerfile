# Use the latest Nginx image as a base
FROM nginx:latest

# Copy the Nginx configuration files
COPY default.conf /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/default.conf.template
COPY swap_ports.sh /etc/nginx/swap_ports.sh
RUN chmod +x /etc/nginx/swap_ports.sh

# Create webroot
RUN mkdir -p /var/www/html && echo '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>?</title></head><body><p>A page...</p></body></html>' > /var/www/html/index.html

# Copy the certificate generation script
RUN mkdir -p /etc/nginx/ssl
COPY openssl.cnf /etc/nginx/ssl/openssl.cnf
COPY create-certs.sh /etc/nginx/create-certs.sh

# Regen certs if needed
RUN chmod +x /etc/nginx/create-certs.sh && /etc/nginx/create-certs.sh

# Start Nginx
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
