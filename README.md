# ArtifactToolkit

ArtifactToolkit is a containerized security service designed to facilitate pentesting engagements. It provides a seamless 
environment for sharing artifacts and tools, including a Joplin note instance, NFS, and a Git repository. Users authenticate 
through a custom SSH listener to gain access to the services.

## Components

1. **Joplin Server**: A containerized Joplin server for note-taking and collaboration.
2. **Nginx Reverse Proxy**: Provides SSL support using a self-signed certificate.
3. **NFS Container**: Enables network file sharing, mapping to a Docker volume.
4. **PostgreSQL Container**: Supports the Joplin server with a PostgreSQL instance.
5. **Custom SSH Listener**: Authenticates users and whitelists them for the services.

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

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```
## Configuration

Ports: All exposed services are on custom ports over 25,000 to avoid conflicts with existing services.
NFS: Utilizes a Docker volume for shared storage.
Nginx: Generates a self-signed certificate on boot-up if one doesn't exist.
