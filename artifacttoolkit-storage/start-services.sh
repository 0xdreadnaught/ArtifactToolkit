#!/bin/bash

# Start rpcbind and NFS services
mount -t nfsd nfsd /proc/fs/nfsd
/usr/sbin/rpcbind
/usr/sbin/rpc.statd
/usr/sbin/rpc.nfsd --debug 8 --no-udp --nfs-version 4

# Start Samba services
/usr/sbin/nmbd -D
/usr/sbin/smbd -D

# Keep the container running
tail -f /dev/null

