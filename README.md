# Artifact Toolkit

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Reference Output](#reference-output)
- [Components](#components)
  - [ATK-Auth](#artifacttoolkit-auth)
  - [ATK-Ingest](#artifacttoolkit-ingest)
  - [ATK-Nessus](#artifacttoolkit-nessus)
  - [ATK-BH](#artifacttoolkit-bloodhound)
  - [ATK-BH-DB](#artifacttoolkit-bloodhound-database)
  - [ATK-BH-Graph-DB](#artifacttoolkit-bloodhound-graph-database)
- [Development](#development)

## Overview
Artifact Toolkit is a collection of Dockerized services focusing on secure sharing of artifacts and tools during a pentesting engagement. One member of the team will host the services, while the other members hook in to share/pull as needed. All user sessions are invalidated on boot (adjustable time limit pending). The primary service is Krypt-Server, a PKI/JSON based authentication service running in the artifacttoolkit-auth container. [Pending:] After the user authenticates with the Krypt server and receives a valid session, their IP is whitelisted with the other services.

## Features
- PKI-based authentication.
- JSON data storage for user metadata.
- SSL Ingest proxy.
- Nessus scanner for standalone use or SC integration (requires license).
- Extensible architecture for future services.

  [![Codacy Security Scan](https://github.com/0xdreadnaught/ArtifactToolkit/actions/workflows/codacy.yml/badge.svg)](https://github.com/0xdreadnaught/ArtifactToolkit/actions/workflows/codacy.yml)

  [![Bandit](https://github.com/0xdreadnaught/ArtifactToolkit/actions/workflows/bandit.yml/badge.svg)](https://github.com/0xdreadnaught/ArtifactToolkit/actions/workflows/bandit.yml)

## Prerequisites
### Server
- [Docker](https://www.docker.com/)/[Podman](https://podman.io/)
- [Docker-Compose](https://docs.docker.com/compose/)/[Podman-Compose](https://github.com/containers/podman-compose)

### Client
- [SSH](https://www.ssh.com/academy/ssh) (pending custom binary)

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/0xdreadnaught/ArtifactToolkit.git
    ```
2. Copy `.env-sample` to `.env` and update the environment variables as needed.
    ```bash
    cp .env-sample .env
    ```
3. Build and run the Docker services:
    ```bash
    docker-compose up -d
    ```
4. Add users to `user_data.json` (optional).

## Usage

### Login
To log in, use the following command:
```bash
ssh -p 2222 username@server_address login
```
This will authenticate you and grant access to other services.

### List Users [authenticated]
To list all registered and pending users, use:
```bash
ssh -p 2222 username@server_address list-users
```

### List Keys [authenticated]
To list all your public keys stored on the server, use:
```bash
ssh -p 2222 username@server_address list-keys
```

### Prune Keys [authenticated]
To remove all unused keys, use: 
```bash
ssh -p 2222 username@server_address prune-keys
```
**Note**: Thid will delete all but the currently active key.

### Purge Keys [authenticated]
To remove all your stored keys, use:
```bash
ssh -p 2222 username@server_address purge-keys
```
**Note**: This will remove all your keys, and you'll need to re-upload them for future authentication.

### Remove Keys [authenticated]
To remove a specified key, use: 
```bash
ssh -p 2222 username@server_address remove-key <ID#>
```
**Note**: This will not remove the active key.

## Reference Output
### User Registration
![show registration](imgs/atk-registration.png)
### User Login
![show login](imgs/atk-valid-login.png)
### Duplicate Login
![show duplicate login](imgs/atk-duplicate-login.png)
### Invalid Login
![show invalid login](imgs/atk-invalid-login.png)
### Missing Key
![show missing key](imgs/atk-missing-key.png)
### Malformed Command
![show malformed command](imgs/atk-malformed-cmd.png)


## Components

### ArtifactToolkit-Auth
This container runs the Krypt-Server, The authentication gateway for ATK. While piggybacking off SSH, it does not rely on the user to be known to the underlying SSH service. Nor does it allow the user to access a session or channel at any time.

### ArtifactToolkit-Ingest
This container runs an Nginx reverse proxy for data ingestion. It acts as an intermediary for requests from clients seeking resources from other services. SSL certificates are generated as needed, the settings for the certificate can be altered in openssl.cnf.

### ArtifactToolkit-Nessus
This container runs the Nessus scanner, which can be used for standalone scanning or integrated into a Security Center (SC). A license is required for full functionality.

### ArtifactToolkit-Bloodhound
This is the main Bloodhound Community Edition container. The temp password is displayed during the build process. 

### ArtifactToolkit-Bloodhound-Database
This container runs a PostgreSQL backend for Bloodhound's domain data.

### ArtifactToolkit-Bloodhound-Graph-Database
This container runs the Neo4j backend for bloodhound graphing capabilities.

## Development
Debating on adding in automated Nessus configuration modes using the `.env` and Selenium-headless. Still need a note solution. May stick with Joplin just for ease of use. Though it does run the risk of file lock conflicts if poor note structuring is used. Obsidian is deceptive trash. HedgeDoc is probably the best solution, but it's raw markdown editing, which slows down engagements. 
