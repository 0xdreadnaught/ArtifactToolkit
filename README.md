# ArtifactToolkit

WIP DO NOT USE

ArtifactToolkit is a containerized security service designed to facilitate pentesting engagements. 

## Components

1. **NFS Container**: Enables network file sharing, mapping to a Docker volume.

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
   vim ./.env
   ```

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

## Configuration

Users must have an SSH key configured on the AT-SSH listener. Users authenticate while passing a mode, nfs/git/notes/all, and 
are whitelisted by the appropriate services until the system is rebooted. 
