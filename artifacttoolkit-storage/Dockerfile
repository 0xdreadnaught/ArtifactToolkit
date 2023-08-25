FROM quay.io/centos/centos:stream9

RUN yum -y update && \
    yum -y install nfs-utils

COPY start-nfs.sh /start-nfs.sh
COPY exports /etc/exports

EXPOSE 2049

ENTRYPOINT ["/start-nfs.sh"]

