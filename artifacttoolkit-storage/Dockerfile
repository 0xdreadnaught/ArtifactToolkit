FROM centos:9

RUN yum -y update && \
    yum -y install nfs-utils && \
    mkdir -p /opt/shares/tools /opt/shares/artifacts /opt/shares/git && \
    chmod -R 777 /opt/shares

COPY exports /etc/exports

EXPOSE 2049

CMD ["/usr/sbin/rpc.nfsd", "--debug", "8", "--no-udp", "--no-nfs-version", "2", "--no-nfs-version", "3"]
