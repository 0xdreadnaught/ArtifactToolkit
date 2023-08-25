#!/bin/bash

mkdir -p ${TOOLS_PATH} ${ARTIFACTS_PATH} ${GIT_PATH}
chmod -R 777 ${TOOLS_PATH} ${ARTIFACTS_PATH} ${GIT_PATH}

# Start the necessary services for NFS
/usr/sbin/rpcbind
/usr/sbin/rpc.statd
/usr/sbin/rpc.nfsd --debug 8 --no-udp --no-nfs-version 2 --no-nfs-version 3
