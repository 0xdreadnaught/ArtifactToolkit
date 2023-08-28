# Use CentOS 9 as the base image
FROM quay.io/centos/centos:stream9

# Update the system
RUN yum update -y

# Install Python3 and Paramiko
RUN yum install -y python3 python3-pip && \
    pip3 install paramiko

# Expose SSH port
EXPOSE 2222

# Placeholder for the custom script (to be added later)
COPY Krypt-Server.py /opt/Krypt-Server.py

# Run the custom script
CMD python3 /opt/Krypt-Server.py 2>/dev/null
