# ArtifactToolkit

WIP DO NOT USE

ArtifactToolkit is a containerized security service designed to facilitate pentesting engagements. 

## Components

1. **NFS/Samba Container**: Enables network file sharing, mapping to Docker volumes.
2. **Auth Container**: Staged.

## Installation

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/0xdreadnaught/ArtifactToolkit.git
   ```

2. Navigate to the repository directory:
   ```bash
   cd ArtifactToolkit
   ```

3. Configure .env:
   ```bash
   cp ./.env-sample ./.env
   vim ./.env #change settings
   ```

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

## Configuration

Users must have an SSH key configured on the AT-SSH listener. Users authenticate while passing a mode, nfs/git/notes/all, and 
are whitelisted by the appropriate services until the system is rebooted. 

## Container Details

### NFS & SMB Container

This container provides netowrk file share service using both NFS and SMB protocols. It exposes the following ports via .env:

- NFS: 25049
- SMB NetBIOS: 137/udp
- SMB: 445
- SMB Secure: 5445

Volumes are mapped to the following paths:
*These locations are not intended to be changed.

- Tools: /opt/shares/tools
- Artifacts: /opt/shares/artifacts
- Git: /opt/shares/git

