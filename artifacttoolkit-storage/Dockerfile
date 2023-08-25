FROM quay.io/centos/centos:stream9

# Create environment variables
ENV NFS_PORT=2049 \
    SMB_NETBIOS_PORT=137 \
    SMB_PORT=445 \
    SMB_SECURE_PORT=5445 \
    TOOLS_PATH=/opt/shares/tools \
    ARTIFACTS_PATH=/opt/shares/artifacts \
    GIT_PATH=/opt/shares/git

# Install NFS and Samba utilities
RUN yum -y update
RUN yum -y install nfs-utils samba samba-client

# Create directories and set permissions
RUN mkdir -p $TOOLS_PATH $ARTIFACTS_PATH $GIT_PATH && \
    chmod -R 777 $TOOLS_PATH $ARTIFACTS_PATH $GIT_PATH

# Copy exports file for NFS
COPY exports /etc/exports

# Copy Samba configuration file
COPY smb.conf /etc/samba/smb.conf

# Expose NFS and Samba ports
EXPOSE $NFS_PORT $SMB_NETBIOS_PORT/udp $SMB_PORT $SMB_SECURE_PORT

# Copy start script
COPY start-services.sh /start-services.sh
RUN chmod +x /start-services.sh

# Start the necessary services for NFS and Samba and keep the container running
CMD ["/start-services.sh"]

